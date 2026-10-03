# Week 9: Speech-to-Text Customization & RAG Integration

During Week 9 (Sep 22 - Sep 28), we focused heavily on resolving the poor performance of the baseline STT model and began prototyping LLM RAG functionality.

## Accomplishments
- **Custom STT Dataset Collection**: Built a full Flask-based web application (`code/stt_dataset_collector/app.py`) to systematically record, manage, and label custom audio phrases.
- **Catastrophic Forgetting Mitigation**: Successfully fine-tuned the Zipformer STT model on 91 custom audio samples using the `icefall` framework. To prevent the model from collapsing (catastrophic forgetting), we strategically froze the acoustic encoder and only trained the decoder and joiner.
- **STT Evaluation**: Automated STT evaluation metrics with `test_stt.py`, confirming massive improvements in recognizing specific medical intents (e.g., "what medicines do we have").
- **LLM RAG Pipeline**: Integrated Retrieval-Augmented Generation capabilities into `master_controller.py`, allowing the Qwen LLM to query and answer questions about patients and inventory. Built and tested this via `code/test_rag.py` and `code/test_rag_auto.py`.
- **Qualcomm AI Hub / Deployment**: Set up compilation scripts (`compile_qwen_aihub.py`) for optimized hardware inference and moved automated deployment shell scripts into `scripts/` to keep the repo clean.
