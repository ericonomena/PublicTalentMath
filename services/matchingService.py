from sentence_transformers import SentenceTransformer, util
from services import candidatService
from services import offreService

from threading import Thread, Event
from time import sleep
import os

LOCAL_MODEL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "model", "paraphrase-multilingual-MiniLM-L12-v2")
)
# model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
REMOTE_MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model = None
_model_ready = Event()


def _download_and_load_model():
    global _model
    backoffs = [0, 2, 4, 8, 16, 32]
    last_exc = None

    os.environ.setdefault("HF_HOME", "/tmp/hf")
    os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/hf/transformers")
    try:
        os.makedirs(os.environ["HF_HOME"], exist_ok=True)
        os.makedirs(os.environ["TRANSFORMERS_CACHE"], exist_ok=True)
    except Exception:
        pass
    for wait in backoffs:
        try:
            if wait:
                sleep(wait)
            if os.path.isdir(LOCAL_MODEL_DIR):
                print(f"[startup] Trying local model from {LOCAL_MODEL_DIR}")
                _model = SentenceTransformer(LOCAL_MODEL_DIR)
                _model_ready.set()
                print(f"[startup] model ready (local)")
                return
            else:
                print(f"[startup] local model not found at {LOCAL_MODEL_DIR}")
                break
        except Exception as e:
            last_exc = e
            print(f"[startup] local model load retry in {wait}s: {e}")
    print("[startup] Falling back to remote model on Hugging Face Hub")
    for wait in backoffs:
        try:
            if wait:
                sleep(wait)
            _model = SentenceTransformer(REMOTE_MODEL_ID)
            _model_ready.set()
            print(f"[startup] model ready (remote)")
            return
        except Exception as e:
            last_exc = e
            print(f"[startup] remote model init retry in {wait}s: {e}")

    raise RuntimeError(f"[startup] model init failed after retries: {last_exc}")

Thread(target=_download_and_load_model, daemon=True).start()

def _require_model_ready():
    if not _model_ready.is_set():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service initializing, please retry shortly.")

def _get_model():
    _require_model_ready()
    return _model


async def match_offres_for_cv(cv_id, top_n=None):
    _require_model_ready()
    model = _get_model()

    cv_candidat = await candidatService.getCandidatById(cv_id)
    cv_embedding = model.encode(cv_candidat.contenu, convert_to_tensor=True)
    offres = await offreService.getAllOffres()
    offre_texts = [offre.contenu for offre in offres]
    offre_embeddings= model.encode(offre_texts, convert_to_tensor=True)

    """Retourne les offres les plus pertinentes pour un CV donné"""
    scores = util.cos_sim(cv_embedding, offre_embeddings)[0]
    best_idx = scores.argsort(descending=True)

    results = []
    for idx in best_idx:
        score_val = float(scores[idx])
        if score_val != 0:
            offre = offres[idx]
            results.append({
                "offre": offre,
                "score": score_val,
            })
        else:
            break 

    # 5) Limite top_n si demandée
    if top_n is not None:
        return results[:top_n]
    return results




async def match_cvs_for_offre(offre_id, top_n=None):
    print("matching")
    _require_model_ready()
    model = _get_model()

    offre = await offreService.getOffreById(offre_id)
    print("Offre ok")
    cvs = await candidatService.getAllCandidats()
    print("Candidat ok")

    # Encodage
    print("Encodage")
    offre_embedding = model.encode(offre.contenu, convert_to_tensor=True)
    cv_texts = [cv.contenu for cv in cvs]
    cv_embeddings = model.encode(cv_texts, convert_to_tensor=True)

    # Similarités
    print("Similarités")

    scores = util.cos_sim(offre_embedding, cv_embeddings)[0]

    # Tri décroissant
    print("Tri décroissant")
    
    best_idx = scores.argsort(descending=True)

    results = []
    print("Best")

    for idx in best_idx:
        score_val = float(scores[idx])
        if score_val != 0:  
            candidat = cvs[idx]
            results.append({
                "candidat": candidat,
                "score": score_val,
            })
        else:
            break  

    
    if top_n is not None:
        return results[:top_n]
    return results
