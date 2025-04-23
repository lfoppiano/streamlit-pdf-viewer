<template>
  <div id="pdfContainer" :style="pdfContainerStyle">
    <div v-if="args.rendering === 'unwrap'">
      <div id="pdfViewer" :style="pdfViewerStyle"></div>
    </div>
    <div v-else-if="args.rendering === 'legacy_embed'">
      <embed :src="`data:application/pdf;base64,${args.binary}`" :width="`${args.width}`" :height="`${args.height}`"
             type="application/pdf"/>
    </div>
    <div v-else-if="args.rendering === 'legacy_iframe'">
      <embed :src="`data:application/pdf;base64,${args.binary}`" :width="`${args.width}`" :height="`${args.height}`"
             type="application/pdf"/>
    </div>
    <div v-else>
      Error rendering option.
    </div>
  </div>
</template>

<script>
import { onMounted, onUpdated, computed, ref, onUnmounted } from "vue";
import "pdfjs-dist/web/pdf_viewer.css";
import "pdfjs-dist/build/pdf.worker.mjs";
import { getDocument } from "pdfjs-dist/build/pdf";
import { Streamlit } from "streamlit-component-lib";
import * as pdfjsLib from "pdfjs-dist";
import { debounce } from 'lodash';

const CMAP_URL = "pdfjs-dist/cmaps/";
const CMAP_PACKED = true;
const ENABLE_XFA = true;
const acceptedBorderStyleAttributes = ['solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'none', undefined, null];

export default {
  props: ["args"],

  setup(props) {
    const totalHeight = ref(0);
    const maxWidth = ref(0);
    const pageScales = ref([]);
    const pageHeights = ref([]);
    const loadedPages = ref([]);
    const currentFrameHeight = ref(props.args.height || 0);

    const isRenderingAllPages = props.args.pages_to_render.length === 0;

    const renderText = props.args.render_text === true;

    const parseWidthValue = (widthValue, fallbackValue = window.innerWidth) => {
      if (typeof widthValue === "string" && widthValue.endsWith("%")) {
        const num = parseFloat(widthValue)
        if (!isNaN(num)) {
          return { type: "percent", value: num / 100 }
        }
      }
      const numeric = Number(widthValue)
      if (!isNaN(numeric) && numeric > 0) {
        return { type: "pixel", value: numeric }
      }
      return { type: "pixel", value: fallbackValue }
    }

    const pdfContainerStyle = computed(() => {
      const result = parseWidthValue(props.args.width, window.innerWidth);
      const widthCSS = result.type === "percent" ? `${result.value * 100}%` : `${result.value}px`;
      return {
        width: widthCSS,
        height: props.args.height ? `${props.args.height}px` : 'auto',
        overflow: 'auto',
        position: 'relative',
      };
    });

    const pdfViewerStyle = { position: 'relative' };

    const calculatePdfsHeight = (page) => {
      let height = 0;
      if (isRenderingAllPages) {
        for (let i = 0; i < page - 1; i++) {
          height += pageHeights.value[i] * pageScales.value[i] + props.args.pages_vertical_spacing;
        }
      } else {
        for (let i = 0; i < pageHeights.value.length; i++) {
          if (props.args.pages_to_render.includes(i + 1) && i < page - 1) {
            height += pageHeights.value[i] * pageScales.value[i] + props.args.pages_vertical_spacing;
          }
        }
      }
      return height;
    };

    const clearExistingCanvases = (pdfViewer) => {
      if (!pdfViewer) return;
      pdfViewer.innerHTML = '';
    };

    const createCanvasForPage = (page, scale, rotation, pageNumber, resolutionRatioBoost = 1) => {
      const viewport = page.getViewport({ scale, rotation });
      const ratio = (window.devicePixelRatio || 1) * resolutionRatioBoost;

      const canvas = document.createElement("canvas");
      canvas.id = `canvas_page_${pageNumber}`;
      canvas.height = viewport.height * ratio + props.args.pages_vertical_spacing;
      canvas.width = viewport.width * ratio;
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;
      canvas.style.display = "block";
      canvas.style.marginBottom = `${props.args.pages_vertical_spacing}px`;
      canvas.getContext("2d").scale(ratio, ratio);

      return canvas;
    };

    const renderAnnotation = (annotation, pageDiv, scale) => {
      const annotationDiv = document.createElement('div');
      annotationDiv.id = `annotation-${annotation.id || annotation.page}-${annotation.index}`;
      annotationDiv.style.position = 'absolute';
      annotationDiv.style.left = `${annotation.x * scale}px`;
      annotationDiv.style.top = `${annotation.y * scale}px`;
      annotationDiv.style.width = `${annotation.width * scale}px`;
      annotationDiv.style.height = `${annotation.height * scale}px`;
      let border = annotation.border
      if (!annotation.border || !acceptedBorderStyleAttributes.includes(annotation.border)) {
        border = "solid"
      }
      annotationDiv.style.outline = `${props.args.annotation_outline_size * scale}px ${border} ${annotation.color}`;
      annotationDiv.style.cursor = renderText ? 'text' : 'pointer';
      annotationDiv.style.pointerEvents = renderText ? 'none' : 'auto';
      annotationDiv.style.zIndex = 10;

      if (!renderText) {
        annotationDiv.addEventListener('click', () => {
          Streamlit.setComponentValue({
            clicked_annotation: { index: annotation.index, ...annotation },
          });
        });
      }

      pageDiv.appendChild(annotationDiv);
    };

    const renderPage = async (page, canvas, viewport, annotations) => {
      const renderContext = {
        canvasContext: canvas.getContext("2d"),
        viewport: viewport
      };

      await page.render(renderContext).promise;

      const pageDiv = document.createElement('div');
      pageDiv.className = 'page';
      pageDiv.style.position = 'relative';
      pageDiv.style.width = `${viewport.width}px`;
      pageDiv.style.height = `${viewport.height}px`;

      const canvasWrapper = document.createElement('div');
      canvasWrapper.className = 'canvasWrapper';
      canvasWrapper.style.position = 'absolute';
      canvasWrapper.style.top = '0';
      canvasWrapper.style.left = '0';
      canvasWrapper.appendChild(canvas);

      pageDiv.appendChild(canvasWrapper);

      if (renderText) {
        const textContent = await page.getTextContent();
        const textLayerDiv = document.createElement("div");
        textLayerDiv.className = "textLayer";
        textLayerDiv.style.zIndex = "11";
        textLayerDiv.style.position = 'absolute';
        textLayerDiv.style.top = '0';
        textLayerDiv.style.left = '0';
        textLayerDiv.style.height = `${viewport.height}px`;
        textLayerDiv.style.width = `${viewport.width}px`;

        const textLayer = new pdfjsLib.TextLayer({
          textContentSource: textContent,
          container: textLayerDiv,
          viewport: viewport,
          textDivs: []
        });
        await textLayer.render();

        pageDiv.appendChild(textLayerDiv);
      }

      if (annotations && annotations.length > 0) {
        annotations.forEach(annotation => {
          renderAnnotation(annotation, pageDiv, viewport.scale);
        });
      }

      const pdfViewer = document.getElementById("pdfViewer");
      pdfViewer.appendChild(pageDiv);
    };

    const getPagesToRender = (numPages) => {
      if (props.args.pages_to_render.length === 0) {
        return Array.from({ length: numPages }, (_, i) => i + 1);
      }
      return props.args.pages_to_render;
    };

    const renderPdfPages = async (pdf, pdfViewer, pagesToRender) => {
      totalHeight.value = 0;
      pageScales.value = [];
      pageHeights.value = [];
      loadedPages.value = [];

      const resolutionBoost = props.args.resolution_boost || 1;

      for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber);
        const rotation = page.rotate;
        const unscaledViewport = page.getViewport({ scale: 1.0, rotation });

        if (props.args.height > 0) {
          const widthScale = unscaledViewport.width / unscaledViewport.height;
          const possibleScaledWidth = widthScale * props.args.height;
          if (maxWidth.value === 0 || possibleScaledWidth < maxWidth.value) {
            maxWidth.value = possibleScaledWidth;
          }
        }

        const scale = maxWidth.value / unscaledViewport.width;

        pageScales.value.push(scale);
        pageHeights.value.push(unscaledViewport.height);

        if (pagesToRender.includes(pageNumber)) {
          const canvas = createCanvasForPage(page, scale, rotation, pageNumber, resolutionBoost);
          pdfViewer.style.setProperty('--scale-factor', scale);

          const viewport = page.getViewport({
            scale: scale,
            rotation: rotation,
            intent: "print",
          });

          const annotationsForPage = props.args.annotations.filter(
            anno => Number(anno.page) === pageNumber
          );

          totalHeight.value += canvas.height / ((window.devicePixelRatio || 1) * resolutionBoost);
          await renderPage(page, canvas, viewport, annotationsForPage);

          if (canvas.id) {
            loadedPages.value.push(canvas.id);
          }
        }
      }
      // Subtract the margin for the last page as it's not needed
      if (pagesToRender.length > 0) {
        totalHeight.value -= props.args.pages_vertical_spacing;
      }
    };

    const alertError = (error) => {
      window.alert(error.message);
      console.error(error);
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

        const pdfViewer = document.getElementById("pdfViewer");
        clearExistingCanvases(pdfViewer);

        const pagesToRender = getPagesToRender(pdf.numPages);
        await renderPdfPages(pdf, pdfViewer, pagesToRender);
        scrollToItem();
      } catch (error) {
        alertError(error);
      }
    };

    const scrollToItem = () => {
      if (props.args.scroll_to_page) {
        const page = document.getElementById(`canvas_page_${props.args.scroll_to_page}`);
        if (page) {
          page.scrollIntoView({ behavior: "smooth" });
        }
      } else if (props.args.scroll_to_annotation) {
        const annotation = document.querySelector(`[id^="annotation-"][data-index="${props.args.scroll_to_annotation}"]`);
        if (annotation) {
          annotation.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }
    };

    const setFrameHeight = () => {
      const newHeight = props.args.height || totalHeight.value;
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
        newMaxWidth = Math.min(result.value, window.innerWidth);
      }

      if (newMaxWidth !== maxWidth.value) {
        maxWidth.value = newMaxWidth;
      }
    };

    const handleResize = async () => {
      try {
        console.log('handleResize');
        if (props.args.rendering === "unwrap") {
          const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`;
          setFrameWidth();
          await loadPdfs(binaryDataUrl);
          setFrameHeight();
        }
      } catch (error) {
        console.error(error);
      }
    };

    // Debounced resize handler to prevent multiple rapid executions
    const debouncedHandleResize = debounce(handleResize, 200);

    onMounted(() => {
      debouncedHandleResize();
      window.addEventListener("resize", debouncedHandleResize);
    });

    onUnmounted(() => {
      window.removeEventListener("resize", debouncedHandleResize);
    });

    return {
      pdfContainerStyle,
      pdfViewerStyle,
    };
  },
};
</script>