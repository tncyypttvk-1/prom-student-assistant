# Prom model connection
Public temporary Colab URL: https://22e898781647a77e1d.gradio.live

The floating Prom control and AI section CTA open a native dialog containing the real Gradio app in a cross-origin iframe. The model runs in Colab; GitHub Pages hosts only the website. Closing/expiring the Colab runtime can stop the demo. The panel provides an external tab fallback and reconnect control. No API token is exposed.

Update site/dist/demo-config.js with a verified HTTPS gradio.live or hf.space app URL. A Hugging Face model repository or /tree/main/space directory is not an app endpoint. The teacher's permanent hf.space URL can replace the temporary one without changing model or training.

Final Colab: https://colab.research.google.com/drive/1-NL5VZoQhPoZOFM7Hq5MaNHQ85zae99j?usp=sharing

Notebook application score 23.5/30 = 0.7833; TR 0.7333; EN 0.8333. Rule-based GPA routing and agent argument normalization contribute. Three CPU smoke tests were performed; these scores are not CPU benchmark results.
