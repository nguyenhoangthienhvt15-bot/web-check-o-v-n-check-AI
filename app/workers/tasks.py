from app.core.celery_app import celery_app
from app.engines.plagiarism import PlagiarismEngine
from app.engines.ai_detector import BinocularsDetector

plagiarism_engine = PlagiarismEngine()
ai_detector = None

def get_ai_detector():
    global ai_detector
    if ai_detector is None:
        ai_detector = BinocularsDetector()
    return ai_detector

@celery_app.task(bind=True)
def run_full_document_scan(self, doc_text: str):
    self.update_state(state="PROGRESS", meta={"stage": "Checking AI Patterns (Binoculars)"})
    
    detector = get_ai_detector()
    ai_result = detector.compute_score(doc_text)

    self.update_state(state="PROGRESS", meta={"stage": "Querying MinHash LSH Index"})
    candidate_doc_ids = plagiarism_engine.query_similar(doc_text)

    matches = []
    top_similarity = 0.0
    for cand_id in candidate_doc_ids:
        cand_text = plagiarism_engine.corpus_storage.get(cand_id, "")
        if cand_text:
            sim, matched_sents = plagiarism_engine.calculate_sentence_overlap(doc_text, cand_text)
            if sim > 0:
                matches.append({"doc_id": cand_id, "similarity": sim, "overlap_sentences": matched_sents})
                if sim > top_similarity:
                    top_similarity = sim

    return {
        "status": "COMPLETED",
        "ai_detection": ai_result,
        "plagiarism": {
            "candidate_matches_count": len(candidate_doc_ids),
            "max_similarity_score": top_similarity,
            "matches": matches,
        },
    }

