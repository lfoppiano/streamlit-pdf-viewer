<template>
  <div id="pdfViewer" :style="{overflow: 'scroll', height: pdfViewerHeight + 'px'}">
  </div>
</template>

<script>
import { onMounted, onUpdated, ref } from "vue"
import "pdfjs-dist/build/pdf.worker.entry"
import {getDocument} from "pdfjs-dist/build/pdf"
import {Streamlit} from "streamlit-component-lib"


export default {
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  setup(props) {

    // let totalHeight = 0
    // let maxWidth = 0

    const pdfViewerHeight = ref(800) // for debug mode
    try {
      pdfViewerHeight.value = window.parent.innerHeight * 0.85
    } catch (error) {
      // While debugging, the parent window cannot be retrieved due to CORS constraints, so this error occurs.
      console.debug(error)
    }

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
            // if (canvas.width > maxWidth) {
            //   maxWidth = canvas.width
            // }
            // totalHeight = canvas.height

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
      console.debug("Mounted")

      if (props.args?.binary) {
        const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`
        loadPdfs(binaryDataUrl)
      }
      Streamlit.setFrameHeight(pdfViewerHeight.value)
      Streamlit.setComponentReady()
    });

    onUpdated(() => {
      console.debug('Updated')
      // After we're updated, tell Streamlit that our height may have changed.
      // Streamlit.setFrameHeight(pdfViewerHeight.value)
      // Streamlit.setComponentReady()
    });

    return {
      pdfViewerHeight,
    }
  },
}
</script>
