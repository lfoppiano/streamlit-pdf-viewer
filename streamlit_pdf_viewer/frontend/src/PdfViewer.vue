<template>
  <div id="pdfViewer">

  </div>
  <!--    <div>-->
  <!--        <div v-if="htmlStringBinary" style="clear: both;">-->
  <!--&lt;!&ndash;            <embed :src="htmlStringBinary" :width="args.width" :height="args.height" type="application/pdf" />&ndash;&gt;-->
  <!--        </div>-->
  <!--        <div v-else>-->
  <!--            no pdf yet-->
  <!--            {{args.binary.length}}-->
  <!--            {{htmlStoringBinary}}-->
  <!--        </div>-->
  <!--    </div>-->
</template>

<script>
import { onMounted, onUpdated } from "vue"
import "pdfjs-dist/build/pdf.worker.entry"
import { getDocument } from "pdfjs-dist/build/pdf"
import { useStreamlit } from "./streamlit"
import { Streamlit } from "streamlit-component-lib"


export default {
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  setup(props) {
    // useStreamlit() // lifecycle hooks for automatic Streamlit resize
    // const htmlStringBinary = ref('');

    let totalHeight = 0
    let maxWidth = 0
    const loadPdfs = async (url) => {
      try {
        const loadingTask = await getDocument(url)
        const pdfViewer = document.getElementById("pdfViewer")
        const canvases = pdfViewer?.getElementsByTagName("canvas")

        for (let j = canvases.length - 1; j >= 0; j--) {
          pdfViewer?.removeChild(canvases.item(j))
        }

        loadingTask.promise.then(async function(pdf) {
          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i)
            const viewport = page.getViewport({ scale: 1 })
            const canvas = document.createElement("canvas")
            const context = canvas.getContext("2d")
            pdfViewer?.append(canvas)
            canvas.height = viewport.height
            canvas.width = viewport.width
            if (canvas.width > maxWidth) {
              maxWidth = canvas.width
            }
            totalHeight +=  canvas.height

            console.log(canvas.height)
            console.log(canvas.width)
            canvas.style.display = "block"

            const renderContext = {
              canvasContext: context,
              viewport: viewport,
            }
            const renderTask = page.render(renderContext)
            renderTask.promise.then(function() {
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
    // props.binaryが変更されたときに呼び出される
    // watch(() => props.args?.binary, (newBinary) => {
    //     if (newBinary) {
    //       console.log("bao miao ciao")
    //         const binaryDataUrl = `data:application/pdf;base64,${newBinary}`;
    //         loadPdfs(binaryDataUrl);
    //     }
    // }, { immediate: true });

    onMounted(() => {
      console.log(props.args?.width)
      console.log(props.args?.height)
      if (props.args?.binary) {
        const binaryDataUrl = `data:application/pdf;base64,${props.args.binary}`
        loadPdfs(binaryDataUrl)
      }
      Streamlit.setFrameHeight(totalHeight)
      Streamlit.setComponentReady()
    });

    onUpdated(() => {
      console.log(props.args?.width)
      console.log(props.args?.height)
      // After we're updated, tell Streamlit that our height may have changed.
      Streamlit.setFrameHeight(totalHeight)
    });

    return {
      width: props.args?.width,
      height: props.args?.height,
    }
  },
}
</script>
