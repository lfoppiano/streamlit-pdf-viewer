<template>
  <div id="pdfContainer" :style="pdfContainerStyle">
    <div id="pdfViewer" :style="pdfViewerStyle">
      <div id="pdfAnnotations" v-if="args.annotations">
        <div v-for="(annotation, index) in args.annotations" :key="index" :style="getPageStyle">
          <div :style="getAnnotationStyle(annotation)" :id="`annotation-${index}`"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {onMounted, onUpdated, computed, ref} from "vue";
import "pdfjs-dist/build/pdf.worker.entry";
import {getDocument} from "pdfjs-dist/build/pdf";
import {Streamlit} from "streamlit-component-lib";

export default {
  props: ["args"],

  setup(props) {
    const totalHeight = ref(0);
    const maxWidth = ref(0);
    const pageScales = ref([]);
    const pageHeights = ref([]);
    const pageMargin = 2; // Set the margin between PDF pages to 2 pixels


    const pdfContainerStyle = computed(() => ({
      width: `${props.args.width}px`,
      height: props.args.height ? `${props.args.height}px` : 'auto',
      overflow: 'auto',
    }));

    const pdfViewerStyle = {position: 'relative'};
    const getPageStyle = {position: 'relative'};

    const calculatePdfsHeight = (page) => {
      const pageIndex = page - 1;
      let height = 0;
      for (let i = 0; i < pageIndex; i++) {
        height += Math.floor(pageHeights.value[i] * pageScales.value[i]) + props.args.pages_vertical_spacing; // Add margin for each page
      }
      return height;
    };


    const getAnnotationStyle = (annoObj) => {
      const scale = pageScales.value[annoObj.page - 1];
      return {
        position: 'absolute',
        left: `${annoObj.x * scale}px`,
        top: `${calculatePdfsHeight(annoObj.page) + annoObj.y * scale}px`,
        width: `${annoObj.width * scale}px`,
        height: `${annoObj.height * scale}px`,
        outline: `${props.args.annotation_outline_size * scale}px solid`,
        outlineColor: annoObj.color,
        cursor: 'pointer'
      };
    };

    const clearExistingCanvases = (pdfViewer) => {
      const canvases = pdfViewer?.getElementsByTagName("canvas");
      for (let j = canvases.length - 1; j >= 0; j--) {
        pdfViewer?.removeChild(canvases.item(j));
      }
    };

    const createCanvasForPage = (page, scale, rotation) => {
      const viewport = page.getViewport({scale, rotation});
      const canvas = document.createElement("canvas");
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      canvas.style.display = "block";
      canvas.style.marginBottom = `${props.args.pages_vertical_spacing}px`;
      return canvas;
    };


    const renderPage = async (page, canvas) => {
      const renderContext = {
        canvasContext: canvas.getContext("2d"),
        viewport: page.getViewport({scale: pageScales.value[page._pageIndex], rotation: page.rotate}),
      };
      const renderTask = page.render(renderContext);
      await renderTask.promise;
    };

    const renderPdfPages = async (pdf, pdfViewer) => {
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const rotation = page.rotate;
        const actualViewport = page.getViewport({scale: 1.0, rotation: rotation});
        const scale = props.args.width / actualViewport.width;
        pageScales.value.push(scale);
        pageHeights.value.push(actualViewport.height);

        const canvas = createCanvasForPage(page, scale, rotation);
        pdfViewer?.append(canvas);

        if (canvas.width > maxWidth.value) {
          maxWidth.value = canvas.width;
        }
        totalHeight.value += canvas.height;
        totalHeight.value += props.args.pages_vertical_spacing;
        await renderPage(page, canvas);
      }
      // Subtract the margin for the last page as it's not needed
      totalHeight.value -= props.args.pages_vertical_spacing;
    };


    const alertError = (error) => {
      window.alert(error.message);
      console.error(error);
    };

    const loadPdfs = async (url) => {
      try {
        const loadingTask = await getDocument(url);
        const pdfViewer = document.getElementById("pdfViewer");
        clearExistingCanvases(pdfViewer);

        const pdf = await loadingTask.promise;
        await renderPdfPages(pdf, pdfViewer);
      } catch (error) {
        alertError(error);
      }
    };


    const setFrameHeight = () => {
      Streamlit.setFrameHeight(props.args.height || totalHeight.value);
      Streamlit.setComponentReady();
    };

    onMounted(() => {
      const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`;
      loadPdfs(binaryDataUrl);
      setFrameHeight();
    });

    onUpdated(setFrameHeight);

    return {
      getAnnotationStyle,
      pdfContainerStyle,
      pdfViewerStyle,
      getPageStyle
    };
  },
};
</script>
