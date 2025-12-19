<template>
  <div :style="pdfContainerStyle" ref="pdfContainer" id="pdfContainer" class="container-wrapper">
    <div class="scrolling-container">
      <div id="pdfViewer" :style="{ '--scale-factor': currentZoom }">
        <div
            v-for="page in pages"
            :key="page.pageNumber"
            class="page"
            :style="{
            width: `${page.viewport.width}px`,
            height: `${page.viewport.height}px`,
            marginBottom: `${args.pages_vertical_spacing}px`,
            borderBottom: args.show_page_separator ? '1px solid #ddd' : 'none',
            position: 'relative'
          }"
        >
          <div class="canvasWrapper" :style="{ position: 'absolute', top: 0, left: 0 }">
            <canvas
                :ref="(el) => { if (el) pageCanvasRefs[page.pageNumber] = el }"
                :id="`canvas_page_${page.pageNumber}`"
                :width="page.width"
                :height="page.height"
                :style="{
                width: `${page.viewport.width}px`,
                height: `${page.viewport.height}px`,
                display: 'block'
              }"
            ></canvas>
          </div>

          <div
              v-if="renderText"
              class="textLayer"
              :style="{
              zIndex: 11,
              position: 'absolute',
              top: 0,
              left: 0,
              height: `${page.viewport.height}px`,
              width: `${page.viewport.width}px`
            }"
              :ref="(el) => { if (el) pageTextLayerRefs[page.pageNumber] = el }"
          ></div>

          <div v-if="page.annotations && page.annotations.length > 0">
            <div
                v-for="annotation in page.annotations"
                :key="annotation.id"
                :id="`annotation-${annotation.id}`"
                :data-index="annotation.id"
                :style="{
                position: 'absolute',
                left: `${annotation.x * page.scale}px`,
                top: `${annotation.y * page.scale}px`,
                width: `${annotation.width * page.scale}px`,
                height: `${annotation.height * page.scale}px`,
                outline: `${args.annotation_outline_size * page.scale}px ${annotation.borderStyle} ${annotation.color}`,
                cursor: renderText ? 'text' : 'pointer',
                pointerEvents: renderText ? 'none' : 'auto',
                zIndex: 10
              }"
                @click="!renderText && handleAnnotationClick(annotation)"
            ></div>
          </div>
        </div>
      </div>
    </div>
    <div class="zoom-controls">
      <button class="zoom-button" @click.stop="toggleZoomPanel">
        {{ Math.round(currentZoom * 100) }}%
      </button>
      <div v-if="showZoomPanel" class="zoom-panel">
        <div class="zoom-input-container">
          <input
              type="number"
              class="zoom-input"
              v-model="manualZoomInput"
              @keyup.enter="applyManualZoom"
              @blur="applyManualZoom"
          />
          <span class="zoom-input-percent">%</span>
        </div>
        <div class="zoom-separator"></div>
        <button class="zoom-option" @click="zoomIn">
          <span class="zoom-icon">+</span> Zoom In
        </button>
        <button class="zoom-option" @click="zoomOut">
          <span class="zoom-icon">−</span> Zoom Out
        </button>
        <div class="zoom-separator"></div>
        <button class="zoom-option" @click="fitToWidth">
          <span class="zoom-icon">↔</span> Fit to Width
        </button>
        <button class="zoom-option" @click="fitToHeight">
          <span class="zoom-icon">↕</span> Fit to Height
        </button>
        <button
            v-for="preset in zoomPresets"
            :key="preset"
            class="zoom-option zoom-preset"
            :class="{ active: Math.abs(currentZoom - preset) < 0.01 }"
            @click="setZoom(preset)"
        >
          {{ Math.round(preset * 100) }}%
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {onMounted, computed, ref, onUnmounted, watch, nextTick, markRaw} from "vue";
import "pdfjs-dist/web/pdf_viewer.css";
import "pdfjs-dist/build/pdf.worker.mjs";
import {getDocument} from "pdfjs-dist/build/pdf";
import {Streamlit} from "streamlit-component-lib";
import * as pdfjsLib from "pdfjs-dist";
import {debounce} from 'lodash';

const CMAP_URL = "pdfjs-dist/cmaps/";
const CMAP_PACKED = true;
const ENABLE_XFA = true;
const acceptedBorderStyleAttributes = ['solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'none', undefined, null];

export default {
  props: ["args"],

  setup(props) {
    const totalHeight = ref(0);
    const maxWidth = ref(0);
    const pages = ref([]);
    const pageCanvasRefs = ref({});
    const pageTextLayerRefs = ref({});
    const currentFrameHeight = ref(props.args.height || 0);
    const showZoomPanel = ref(false);

    const initialZoom = props.args.zoom_level === null || props.args.zoom_level === undefined ? 'auto' : props.args.zoom_level;
    const localZoomLevel = ref(initialZoom);
    const currentZoom = ref(1); // Will be updated on render

    const zoomPresets = [0.5, 0.75, 1, 1.25, 1.5, 2];
    const pdfInstance = ref(null);
    const pdfContainer = ref(null);
    const manualZoomInput = ref(100);
    const isRendering = ref(false);

    const renderText = props.args.render_text === true;

    const parseWidthValue = (widthValue, fallbackValue = window.innerWidth) => {
      if (typeof widthValue === "string" && widthValue.endsWith("%")) {
        const num = parseFloat(widthValue)
        if (!isNaN(num)) {
          return {type: "percent", value: num / 100}
        }
      }
      const numeric = Number(widthValue)
      if (!isNaN(numeric) && numeric > 0) {
        return {type: "pixel", value: numeric}
      }
      return {type: "pixel", value: fallbackValue}
    }

    const pdfContainerStyle = computed(() => {
      const result = parseWidthValue(props.args.width, window.innerWidth);
      const widthCSS = result.type === "percent" ? `${result.value * 100}%` : `${result.value}px`;
      const style = {
        width: widthCSS,
        height: props.args.height ? `${props.args.height}px` : 'auto',
        position: 'relative',
      };

      const align = props.args.viewer_align || 'center';
      if (align === 'center') {
        style.marginLeft = 'auto';
        style.marginRight = 'auto';
      } else if (align === 'left') {
        style.marginLeft = '0';
        style.marginRight = 'auto';
      } else if (align === 'right') {
        style.marginLeft = 'auto';
        style.marginRight = '0';
      }

      return style;
    });

    const handleAnnotationClick = (annotation) => {
      Streamlit.setComponentValue({
        clicked_annotation: {index: annotation.id, ...annotation},
      });
    };

    const getPagesToRender = (numPages) => {
      if (props.args.pages_to_render.length === 0) {
        return Array.from({length: numPages}, (_, i) => i + 1);
      }
      return props.args.pages_to_render;
    };

    const renderPdfPages = async (pdf, pagesToRender) => {
      totalHeight.value = 0;
      pages.value = [];
      pageCanvasRefs.value = {};
      pageTextLayerRefs.value = {};

      const resolutionBoost = props.args.resolution_boost || 1;
      let maxPageWidth = 0;

      // Determine the final scale for all pages
      const firstPage = await pdf.getPage(1);
      const unscaledViewport = firstPage.getViewport({scale: 1.0});
      let finalScale;
      if (localZoomLevel.value === 'auto') {
        finalScale = (maxWidth.value / unscaledViewport.width) * 0.98; // Fit to width
      } else if (localZoomLevel.value === 'auto-height') {
        const containerHeight = pdfContainer.value.clientHeight;
        // If no height is specified or container height is too small, fall back to fit-to-width
        if (!props.args.height || containerHeight < 50) {
          finalScale = (maxWidth.value / unscaledViewport.width) * 0.98; // Fit to width
        } else {
          finalScale = (containerHeight / unscaledViewport.height) * 0.98; // Fit to height
        }
      } else {
        finalScale = localZoomLevel.value; // Use numeric zoom
      }
      currentZoom.value = finalScale;
      manualZoomInput.value = Math.round(finalScale * 100);

      let annotationCount = 0;

      const newPages = [];

      for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        if (pagesToRender.includes(pageNumber)) {
          const page = await pdf.getPage(pageNumber);
          const rotation = page.rotate;
          const viewport = page.getViewport({scale: finalScale, rotation});
          const ratio = (window.devicePixelRatio || 1) * resolutionBoost;

          if (viewport.width > maxPageWidth) {
            maxPageWidth = viewport.width;
          }

          const annotationsForPage = props.args.annotations.filter(
              anno => Number(anno.page) === pageNumber
          ).map((anno, index) => {
            let border = anno.border;
            if (!anno.border || !acceptedBorderStyleAttributes.includes(anno.border)) {
              border = "solid";
            }
            return {
              ...anno,
              id: anno.id || (annotationCount + index),
              borderStyle: border
            };
          });

          annotationCount += annotationsForPage.length;

          newPages.push({
            pageNumber,
            page: markRaw(page),
            viewport: markRaw(viewport),
            width: viewport.width * ratio,
            height: viewport.height * ratio,
            scale: finalScale,
            annotations: annotationsForPage
          });

          totalHeight.value += viewport.height;
        }
      }

      if (pagesToRender.length > 0) {
        totalHeight.value -= props.args.pages_vertical_spacing; // Adjust for last margin
      }

      pages.value = newPages;

      // Wait for DOM update to render canvases
      await nextTick();

      for (const pageData of pages.value) {
        try {
          const canvas = pageCanvasRefs.value[pageData.pageNumber];
          if (canvas) {
            const renderContext = {
              canvasContext: canvas.getContext("2d"),
              viewport: pageData.viewport,
              transform: [resolutionBoost, 0, 0, resolutionBoost, 0, 0] // Scale for resolution boost
            };
            await pageData.page.render(renderContext).promise;
          }

          if (renderText) {
            const textLayerDiv = pageTextLayerRefs.value[pageData.pageNumber];
            if (textLayerDiv) {
              const textContent = await pageData.page.getTextContent();
              const textLayer = new pdfjsLib.TextLayer({
                textContentSource: textContent,
                container: textLayerDiv,
                viewport: pageData.viewport,
                textDivs: []
              });
              await textLayer.render();
            }
          }
        } catch (error) {
          console.error(`Failed to render page ${pageData.pageNumber}:`, error);
        }
      }
    };

    const alertError = (error) => {
      console.error(error);
      window.alert(error.message);
    };

    const loadPdfs = async (url) => {
      pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/build/pdf.worker.mjs';
      try {
        const loadingTask = getDocument({
          url: url,
          cMapUrl: CMAP_URL,
          cMapPacked: CMAP_PACKED,
          enableXfa: ENABLE_XFA,
        });
        const pdf = await loadingTask.promise;
        pdfInstance.value = pdf;

        const pagesToRender = getPagesToRender(pdf.numPages);
        await renderPdfPages(pdf, pagesToRender);
        scrollToItem();
      } catch (error) {
        alertError(error);
      }
    };

    const scrollToItem = () => {
      if (props.args.scroll_to_page) {
        const page = document.getElementById(`canvas_page_${props.args.scroll_to_page}`);
        if (page) {
          page.scrollIntoView({behavior: "smooth"});
        }
      } else if (props.args.scroll_to_annotation) {
        const annotation = document.querySelector(`[id^="annotation-"][data-index="${props.args.scroll_to_annotation}"]`);
        if (annotation) {
          annotation.scrollIntoView({behavior: "smooth", block: "center"});
        }
      }
    };

    const setFrameHeight = () => {
      const newHeight = props.args.height ? props.args.height : totalHeight.value;
      if (newHeight !== currentFrameHeight.value) {
        Streamlit.setFrameHeight(newHeight);
        currentFrameHeight.value = newHeight;
      }
    };

    const setFrameWidth = () => {
      const result = parseWidthValue(props.args.width, window.innerWidth);
      let newMaxWidth;
      if (result.type === "percent") {
        newMaxWidth = Math.min(Math.floor(result.value * window.innerWidth), window.innerWidth);
      } else {
        newMaxWidth = result.value;
      }

      if (newMaxWidth !== maxWidth.value) {
        maxWidth.value = newMaxWidth;
      }
    };

    const handleResize = async () => {
      if (isRendering.value) return;
      isRendering.value = true;
      try {
        const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`;
        setFrameWidth();
        await loadPdfs(binaryDataUrl);
        setFrameHeight();

      } catch (error) {
        console.error(error);
      } finally {
        isRendering.value = false;
      }
    };

    watch(() => props.args.binary, () => {
      handleResize();
    });

    watch(() => props.args.zoom_level, (newVal) => {
      localZoomLevel.value = newVal === null || newVal === undefined ? 'auto' : newVal;
      handleResize();
    });

    watch(() => props.args.viewer_align, () => {
      handleResize();
    });

    const setZoom = (zoomLevel) => {
      localZoomLevel.value = zoomLevel;
      showZoomPanel.value = false;
      handleResize();
    };

    const zoomIn = () => {
      const newZoom = Math.min(currentZoom.value * 1.2, 10);
      setZoom(newZoom);
    };

    const zoomOut = () => {
      const newZoom = Math.max(currentZoom.value / 1.2, 0.1);
      setZoom(newZoom);
    };

    const fitToWidth = () => {
      setZoom('auto');
    };

    const fitToHeight = async () => {
      // If no height is specified, fall back to fit-to-width
      if (!props.args.height) {
        setZoom('auto');
      } else {
        setZoom('auto-height');
      }
    };

    const toggleZoomPanel = () => {
      showZoomPanel.value = !showZoomPanel.value;
      if (showZoomPanel.value) {
        manualZoomInput.value = Math.round(currentZoom.value * 100);
      }
    };

    const applyManualZoom = () => {
      let zoomValue = parseFloat(manualZoomInput.value);
      if (!isNaN(zoomValue) && zoomValue > 0) {
        // Clamp the zoom value between 10% and 1000%
        zoomValue = Math.max(10, Math.min(zoomValue, 1000));
        setZoom(zoomValue / 100);
      } else {
        // Reset input if invalid
        manualZoomInput.value = Math.round(currentZoom.value * 100);
      }
    };

    const handleClickOutside = (event) => {
      if (showZoomPanel.value && !event.target.closest('.zoom-controls')) {
        showZoomPanel.value = false;
      }
    };

    const debouncedHandleResize = debounce(handleResize, 200);

    onMounted(() => {
      debouncedHandleResize();
      window.addEventListener("resize", debouncedHandleResize);
      document.addEventListener('click', handleClickOutside);
    });

    onUnmounted(() => {
      // Clean up PDF.js resources
      if (pdfInstance.value) {
        pdfInstance.value.destroy();
        pdfInstance.value = null;
      }
      window.removeEventListener("resize", debouncedHandleResize);
      document.removeEventListener('click', handleClickOutside);
    });

    return {
      pdfContainer,
      pdfContainerStyle,
      showZoomPanel,
      currentZoom,
      localZoomLevel,
      zoomPresets,
      manualZoomInput,
      setZoom,
      zoomIn,
      zoomOut,
      fitToWidth,
      fitToHeight,
      toggleZoomPanel,
      applyManualZoom,
      pages,
      pageCanvasRefs,
      pageTextLayerRefs,
      renderText,
      handleAnnotationClick
    };
  },
};
</script>

<style scoped>
.container-wrapper {
  position: relative;
}

.scrolling-container {
  height: 100%;
  overflow: auto;
}

.zoom-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.zoom-button {
  background: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  font-weight: 500;
  transition: background 0.2s;
  margin-bottom: 8px;
}

.zoom-button:hover {
  background: rgba(50, 50, 50, 0.9);
}

.zoom-panel {
  background: rgba(25, 25, 25, 0.95);
  backdrop-filter: blur(5px);
  border-radius: 8px;
  padding: 8px;
  width: 200px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.zoom-input-container {
  display: flex;
  align-items: center;
  padding: 4px 8px;
}

.zoom-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px;
  font-size: 14px;
  border-radius: 4px;
  text-align: right;
  -moz-appearance: textfield;
}

.zoom-input::-webkit-outer-spin-button,
.zoom-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.zoom-input-percent {
  color: white;
  margin-left: 8px;
}

.zoom-option {
  display: flex;
  align-items: center;
  width: 100%;
  background: transparent;
  border: none;
  color: white;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  text-align: left;
  border-radius: 4px;
  transition: background 0.2s;
}

.zoom-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.zoom-option.active {
  background: rgba(255, 255, 255, 0.2);
}

.zoom-preset {
  justify-content: center;
}

.zoom-icon {
  display: inline-block;
  width: 24px;
  margin-right: 8px;
  font-weight: bold;
  text-align: center;
}

.zoom-separator {
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
  margin: 8px 0;
}
</style>
