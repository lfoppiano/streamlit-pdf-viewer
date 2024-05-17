<template>
  <div id="pdfContainer" :style="pdfContainerStyle">
    <div v-if="args.rendering==='unwrap'">
      <div id="pdfViewer" :style="pdfViewerStyle">
        <!--        <div class="urlsAnnotations"></div>-->
        <div id="pdfAnnotations" v-if="args.annotations">
          <div v-for="(annotation, index) in filteredAnnotations" :key="index" :style="getPageStyle">
            <div :style="getAnnotationStyle(annotation)" :id="`annotation-${index}`"></div>
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

    const isRenderingAllPages = props.args.pages_to_render.length === 0;

    const filteredAnnotations = computed(() => {
      if (isRenderingAllPages) {
        return props.args.annotations;
      }
      const filteredAnnotations = props.args.annotations.filter(anno => {
        return props.args.pages_to_render.includes(Number(anno.page))
      })
      return filteredAnnotations;
    });

    const pdfContainerStyle = computed(() => ({
      width: props.args.width ? `${props.args.width}px` : `${maxWidth.value}px`,
      height: props.args.height ? `${props.args.height}px` : 'auto',
      overflow: 'auto',
    }));

    const pdfViewerStyle = {position: 'relative'};
    const getPageStyle = {position: 'relative'};

    const calculatePdfsHeight = (page) => {
      let height = 0;
      if (isRenderingAllPages) {
        for (let i = 0; i < page - 1; i++) {
          height += Math.floor(pageHeights.value[i] * pageScales.value[i]) + props.args.pages_vertical_spacing; // Add margin for each page
        }
      } else {
        for (let i = 0; i < pageHeights.value.length; i++) {
          if (props.args.pages_to_render.includes(i + 1) && i < page - 1) {
            height += Math.floor(pageHeights.value[i] * pageScales.value[i]) + props.args.pages_vertical_spacing;
          }
        }
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

    const createCanvasForPage = (page, scale, rotation, pageNumber) => {
      const viewport = page.getViewport({scale, rotation});

      const ratio = window.devicePixelRatio || 1

      const canvas = document.createElement("canvas");
      canvas.id = `canvas_page_${pageNumber}`;
      canvas.height = viewport.height * ratio + props.args.pages_vertical_spacing;
      canvas.width = viewport.width * ratio;
      canvas.style.width = viewport.width + 'px';
      canvas.style.height = viewport.height + 'px';
      canvas.style.display = "block";
      canvas.style.marginBottom = `${props.args.pages_vertical_spacing}px`;
      canvas.getContext("2d").scale(ratio, ratio);
      return canvas;
    };


    const renderPage = async (page, canvas) => {
      const renderContext = {
        canvasContext: canvas.getContext("2d"),
        viewport: page.getViewport({
          scale: pageScales.value[page._pageIndex],
          rotation: page.rotate,
          intent: "print",
        })
      };

      const renderTask = page.render(renderContext);
      await renderTask.promise;
    };

    const renderPdfPages = async (pdf, pdfViewer, pagesToRender = null) => {
      if (pagesToRender.length === 0) {
        pagesToRender = []
        for (let i = 0; i < pdf.numPages; i++) {
          pagesToRender.push(i + 1);
        }
      }

      for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber)
        const rotation = page.rotate
        // Initial viewport
        const unscaledViewport = page.getViewport({
          scale: 1.0,
          rotation: rotation,
        })

        const scale = maxWidth.value / unscaledViewport.width

        pageScales.value.push(scale)
        pageHeights.value.push(unscaledViewport.height)
        if (pagesToRender.includes(pageNumber)) {
          const canvas = createCanvasForPage(page, scale, rotation, pageNumber)
          pdfViewer?.append(canvas)

          const ratio = window.devicePixelRatio || 1
          totalHeight.value += canvas.height / ratio
          await renderPage(page, canvas)
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
      try {
        const loadingTask = await getDocument(url);
        const pdfViewer = document.getElementById("pdfViewer");
        clearExistingCanvases(pdfViewer);

        const pdf = await loadingTask.promise;
        await renderPdfPages(pdf, pdfViewer, props.args.pages_to_render);
      } catch (error) {
        alertError(error);
      }
    };


    const setFrameHeight = () => {
      Streamlit.setFrameHeight(props.args.height || totalHeight.value);
    };

    const setFrameWidth = () => {
      if (props.args.width === null || props.args.width === undefined) {
        maxWidth.value = window.innerWidth
      } else if (Number.isInteger(props.args.width)) {
        maxWidth.value = props.args.width

        // If the desired width is larger than the available inner width,
        // we should not exceed it. To be revised
        if (window.innerWidth < maxWidth.value) {
          maxWidth.value = window.innerWidth
        }
      }
    }

    onMounted(() => {
      const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`;
      setFrameWidth();
      if (props.args.rendering === "unwrap") {
        loadPdfs(binaryDataUrl)
          .then(setFrameHeight)
          .then(Streamlit.setComponentReady);
      } else {
        setFrameHeight();
        Streamlit.setComponentReady();
      }
    });

    onUpdated(() => {
      setFrameHeight();
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
