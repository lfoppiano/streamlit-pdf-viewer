<template>
  <div id="pdfContainer" :style="pdfContainerStyle">
    <div v-if="args.rendering==='unwrap'">
      <div id="pdfViewer" :style="pdfViewerStyle">
      <div id="pdfAnnotations" v-if="args.annotations">
        <div v-for="(annotation, index) in filteredAnnotations" :key="index" :style="getPageStyle">
          <div :style="getAnnotationStyle(annotation, index)" :id="`annotation-${index}`"></div>
        </div>
      </div>
      </div>
    </div>
    <div v-else-if="args.rendering==='legacy_embed'">
      <embed :src="`data:application/pdf;base64,${args.binary}`" :width="`${args.width}`" :height="`${args.height}`" type="application/pdf"/>
    </div>
    <div v-else-if="args.rendering==='legacy_iframe'">
      <embed :src="`data:application/pdf;base64,${args.binary}`" :width="`${args.width}`" :height="`${args.height}`" type="application/pdf"/>
    </div>
    <div v-else>
      Error rendering option.
    </div>
  </div>
</template>

<script>
import { onMounted, onUpdated, computed, ref} from "vue";
import "pdfjs-dist/web/pdf_viewer.css";
import "pdfjs-dist/build/pdf.worker.mjs";
import {getDocument} from "pdfjs-dist/build/pdf";
import {Streamlit} from "streamlit-component-lib";
import * as pdfjsLib from "pdfjs-dist";

const CMAP_URL = "pdfjs-dist/cmaps/";
const CMAP_PACKED = true;
const ENABLE_XFA = true;

export default {
  props: ["args"],

  setup(props) {
    const totalHeight = ref(0);
    const maxWidth = ref(0);
    const pageScales = ref([]);
    const pageHeights = ref([]);
    const loadedPages = ref([]);
    const loadedAnnotations = ref([]);

    const isRenderingAllPages = props.args.pages_to_render.length === 0;

    const filteredAnnotations = computed(() => {
      if (isRenderingAllPages) {
        return props.args.annotations;
      }
      return props.args.annotations.filter(anno => {
        return props.args.pages_to_render.includes(Number(anno.page))
      })
    });

    const renderText = props.args.render_text === true

    const pdfContainerStyle = computed(() => {
      const getStyleValue = (value, defaultValue) => {
        if (typeof value === 'string' && value.endsWith('%')) {
          return value; // Use percentage as is
        } else if (typeof value === 'number' || (typeof value === 'string' && /^\d+$/.test(value))) {
          return `${value}px`; // Append 'px' for numeric values
        }
        return defaultValue; // Use default if value is not valid
      };

      return {
        width: getStyleValue(props.args.width, `${maxWidth.value}px`),
        height: props.args.height ? `${props.args.height}px` : 'auto',
        overflow: 'auto',
      };
    });

    const pdfViewerStyle = {position: 'relative'};
    const getPageStyle = {position: 'relative'};

    const calculatePdfsHeight = (page) => {
      let height = 0;
      if (isRenderingAllPages) {
        for (let i = 0; i < page - 1; i++) {
          height += pageHeights.value[i] * pageScales.value[i] + props.args.pages_vertical_spacing; // Add margin for each page
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

    const getAnnotationStyle = (annoObj, index) => {
      const scale = pageScales.value[annoObj.page - 1];
      const obj = {
        position: 'absolute',
        left: `${annoObj.x * scale}px`,
        top: `${calculatePdfsHeight(annoObj.page) + annoObj.y * scale}px`,
        width: `${annoObj.width * scale}px`,
        height: `${annoObj.height * scale}px`,
        outline: `${props.args.annotation_outline_size * scale}px solid`,
        outlineColor: annoObj.color,
        cursor: 'pointer',
        'z-index': 1
      };
      if (index) {
        loadedAnnotations.value.push(`annotation-${index}`);
      }
      return obj
    };

    const clearExistingCanvases = (pdfViewer) => {
      const canvases = pdfViewer?.getElementsByTagName("canvas");
      for (let j = canvases.length - 1; j >= 0; j--) {
        pdfViewer?.removeChild(canvases.item(j));
      }
    };

    const createCanvasForPage = (page, scale, rotation, pageNumber, resolutionRatioBoost=1) => {
      const viewport = page.getViewport({scale, rotation});

      const ratio = (window.devicePixelRatio || 1) * resolutionRatioBoost
      // console.log(ratio)

      const canvas = document.createElement("canvas");
      canvas.id = `canvas_page_${pageNumber}`;
      canvas.height = viewport.height * ratio + props.args.pages_vertical_spacing;
      canvas.width = viewport.width * ratio;
      canvas.style.width = maxWidth.value + 'px'; // viewport.width + 'px';
      canvas.style.height = viewport.height + 'px';
      canvas.style.display = "block";
      canvas.style.marginBottom = `${props.args.pages_vertical_spacing}px`;
      canvas.getContext("2d").scale(ratio, ratio);
      return canvas;
    };


    const renderPage = async (page, canvas, viewport) => {
      const renderContext = {
        canvasContext: canvas.getContext("2d"),
        viewport: viewport
      };

      try {
        const renderTask = page.render(renderContext);
        await renderTask.promise.catch(function(error){
          // alertError(error);
          // do nothing
        });
      } catch (e) {
        // do nothing
      }


      if (renderText) {
        const textContent = await page.getTextContent();
        const textLayerDiv = document.createElement("div");
        textLayerDiv.className = "textLayer"
        textLayerDiv.style = "z-index: 2"
        // textLayerDiv.style.position = "absolute";
        // textLayerDiv.style.height = `${viewport.height}px`;
        // textLayerDiv.style.width = `${viewport.width}px`;
        const textLayer = new pdfjsLib.TextLayer({
          textContentSource: textContent,
          container: textLayerDiv,
          viewport: viewport,
          textDivs: []
        })
        await textLayer.render()

        requestAnimationFrame(async () => {
          const pageDiv = document.createElement('div');
          pageDiv.className = 'page';

          const canvasWrapper = document.createElement('div');
          canvasWrapper.className = 'canvasWrapper';
          canvasWrapper.appendChild(canvas);

          pageDiv.style = "position: relative;";

          const pdfViewer = document.getElementById("pdfViewer");
          pageDiv.appendChild(canvasWrapper);
          pageDiv.appendChild(textLayerDiv);

          pdfViewer.appendChild(pageDiv);
        });
      } else {
        requestAnimationFrame(() => {
          const pageDiv = document.createElement('div');
          pageDiv.className = 'page';

          const canvasWrapper = document.createElement('div');
          canvasWrapper.className = 'canvasWrapper';
          canvasWrapper.appendChild(canvas);

          pageDiv.style = "position: relative;";
          pageDiv.appendChild(canvasWrapper);
          pdfViewer.appendChild(pageDiv);
        });
      }
    };

    const renderPdfPages = async (pdf, pdfViewer, pagesToRender = null) => {
      if (pagesToRender.length === 0) {
        pagesToRender = []
        for (let i = 0; i < pdf.numPages; i++) {
          pagesToRender.push(i + 1);
        }
      }

      let resolutionBoost = 1
      if (props.args.resolution_boost) {
        resolutionBoost = props.args.resolution_boost
      }

      for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber)
        const rotation = page.rotate
        // Initial viewport
        const unscaledViewport = page.getViewport({
          scale: 1.0,
          rotation: rotation,
        })

        if (props.args.height > 0) {
          const widthScale =  unscaledViewport.width / unscaledViewport.height
          const possibleScaledWidth = widthScale * props.args.height
          if (maxWidth.value === 0) {
            maxWidth.value = possibleScaledWidth
          } else if (possibleScaledWidth < maxWidth.value) {
            maxWidth.value = possibleScaledWidth
          }
        }

        const scale = maxWidth.value / unscaledViewport.width

        pageScales.value.push(scale)
        pageHeights.value.push(unscaledViewport.height)
        if (pagesToRender.includes(pageNumber)) {
          const canvas = createCanvasForPage(page, scale, rotation, pageNumber, resolutionBoost)

          // pdfViewer?.append(canvas)
          pdfViewer.style.setProperty('--scale-factor', scale);

          const viewport = page.getViewport({
            scale: pageScales.value[page._pageIndex],
            rotation: page.rotate,
            intent: "print",
          });

          const ratio = (window.devicePixelRatio || 1) * resolutionBoost
          totalHeight.value += canvas.height / ratio
          await renderPage(page, canvas, viewport)
          if (canvas.id !== undefined) {
            loadedPages.value.push(canvas.id)
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
        const loadingTask = await getDocument({
          url: url,
          cMapUrl: CMAP_URL,
          cMapPacked: CMAP_PACKED,
          enableXfa: ENABLE_XFA,
        });
        const pdfViewer = document.getElementById("pdfViewer");
        clearExistingCanvases(pdfViewer);

        const pdf = await loadingTask.promise;
        await renderPdfPages(pdf, pdfViewer, props.args.pages_to_render);
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
        const annotation = document.getElementById(`annotation-${props.args.scroll_to_annotation - 1}`);
        if (annotation) {
          annotation.scrollIntoView({behavior: "smooth", block: "center"});
        }
      }
    };

    const collectAndReturnIds = () => {
      const pages_ids = new Set()
      const annotations_ids = new Set()

      let j

      for (j = 0; j < loadedAnnotations.value.length; j++) {
        annotations_ids.add(loadedAnnotations.value[j]);
      }
      for (j = 0; j < loadedPages.value.length; j++) {
        pages_ids.add(loadedPages.value[j]);
      }

      // Streamlit.setComponentValue({"pages": Array.from(pages_ids), "annotations": Array.from(annotations_ids)})
    }


    const setFrameHeight = () => {
      Streamlit.setFrameHeight(props.args.height || totalHeight.value);
    };

    const setFrameWidth = () => {
      const { width } = props.args;
      
      const calculateWidth = (widthValue) => {
        if (typeof widthValue === 'string' && widthValue.endsWith('%')) {
          // Handle percentage string
          const percentage = parseFloat(widthValue) / 100;
          return Math.floor(window.innerWidth * percentage);
        } else if (Number.isInteger(Number(widthValue))) {
          // Handle integer value
          return Number(widthValue);
        }
        // Default to full window width if invalid input
        return window.innerWidth;
      };

      if (width === null || width === undefined) {
        maxWidth.value = window.innerWidth;
      } else {
        const calculatedWidth = calculateWidth(width);
        
        // Ensure the calculated width doesn't exceed the window's inner width
        maxWidth.value = Math.min(calculatedWidth, window.innerWidth);
      }
    };

    onMounted(() => {
      const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`;
      setFrameWidth();
      if (props.args.rendering === "unwrap") {
        loadPdfs(binaryDataUrl)
          .then(setFrameHeight)
          .then(collectAndReturnIds)
          // .then(scrollToItem)
          //LF calling setComponentReady seems to be done anyway by the WithStreamlitConnection.vue
          // .then(Streamlit.setComponentReady);
      } else {
        setFrameHeight();
        // Streamlit.setComponentReady();
      }
    });

    onUpdated(() => {
      setFrameHeight();
      setFrameWidth();
      if (props.args.rendering === "unwrap") {
        scrollToItem();
      }
    });


    return {
      filteredAnnotations,
      getAnnotationStyle,
      pdfContainerStyle,
      pdfViewerStyle,
      getPageStyle
    };
  },
};
</script>
