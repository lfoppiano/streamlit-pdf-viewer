<template>
  <div id="pdfViewer">
    <div id="pdfAnnotations" v-if="args.annotations">
      <div v-for="(annotation, index) in args.annotations" :key="index">
        <div :style="getAnnotationStyle(annotation)" :id="index"></div>
      </div>
    </div>
  </div>
</template>

<script>
import {onMounted, onUpdated, ref} from "vue"
import "pdfjs-dist/build/pdf.worker.entry"
import {getDocument} from "pdfjs-dist/build/pdf"
import {Streamlit} from "streamlit-component-lib"


export default {
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  setup(props) {
    console.log(props.args)
    let totalHeight = 0
    let pdfHeight = 0
    let maxWidth = 0

    const getPdfsHeight = (page, ratio = 1) => {
      let height = 0
      for (let i = 1; i < page; i++) {
        height += Math.floor(pdfHeight * ratio)
      }
      return height
    }

    const getAnnotationStyle = (annotation) => ({
      position: 'absolute',
      left: `${annotation.x}px`,
      top: `${getPdfsHeight(annotation.page) + annotation.y}px`,
      width: `${annotation.width}px`,
      height: `${annotation.height}px`,
      outline: '2px solid',
      outlineColor: annotation.color,
      cursor: 'pointer'
    });
    const loadPdfs = async (url) => {
      try {
        const loadingTask = await getDocument(url)
        const pdfViewer = document.getElementById("pdfViewer")
        const canvases = pdfViewer?.getElementsByTagName("canvas")

        for (let j = canvases.length - 1; j >= 0; j--) {
          pdfViewer?.removeChild(canvases.item(j))
        }

        loadingTask.promise.then(async function (pdf) {

          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i)
            const viewport = page.getViewport({scale: 1})
            const canvas = document.createElement("canvas")
            const context = canvas.getContext("2d")
            pdfViewer?.append(canvas)
            canvas.height = viewport.height
            canvas.width = viewport.width
            if (canvas.width > maxWidth) {
              maxWidth = canvas.width
            }
            totalHeight += canvas.height
            pdfHeight = canvas.height

            canvas.style.display = "block"

            const renderContext = {
              canvasContext: context,
              viewport: viewport,
            }
            const renderTask = page.render(renderContext)
            renderTask.promise.then(function () {
              console.log("Page rendered")
            })
            console.log(i)
          }
        })
      } catch (error) {
        window.alert(error.message)
        console.error(error)
      }
    }


    onMounted(() => {
      const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`
      loadPdfs(binaryDataUrl)
      Streamlit.setFrameHeight(totalHeight)
      Streamlit.setComponentReady()
    });

    onUpdated(() => {
      // After we're updated, tell Streamlit that our height may have changed.
      Streamlit.setFrameHeight(totalHeight)
      Streamlit.setComponentReady()
    });

    return {
      getPdfsHeight,
      getAnnotationStyle
    }
  },
}
</script>
