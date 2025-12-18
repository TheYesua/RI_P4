from collections import Counter
from math import log, sqrt


def compute_tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    n = len(tokens)
    if n == 0:
        return {}
    return {term: freq / n for term, freq in counts.items()}


def _compute_df(documents_tokens: dict[str, list[str]]) -> dict[str, int]:
    df = Counter()
    for tokens in documents_tokens.values():
        df.update(set(tokens))
    return dict(df)


def compute_idf(doc_count: int, df: dict[str, int]) -> dict[str, float]:
    return {term: log((doc_count + 1) / (df_t + 1)) + 1.0 for term, df_t in df.items()}


def compute_tfidf(documents_tokens: dict[str, list[str]]) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    df = _compute_df(documents_tokens)
    doc_count = len(documents_tokens)
    idf = compute_idf(doc_count, df)
    tfidf_vectors: dict[str, dict[str, float]] = {}
    for doc_id, tokens in documents_tokens.items():
        tf = compute_tf(tokens)
        tfidf = {term: tf_val * idf[term] for term, tf_val in tf.items()}
        tfidf_vectors[doc_id] = tfidf
    return tfidf_vectors, idf


def compute_doc_norms(tfidf_vectors: dict[str, dict[str, float]]) -> dict[str, float]:
    norms: dict[str, float] = {}
    for doc_id, vec in tfidf_vectors.items():
        s = sum(weight * weight for weight in vec.values())
        norms[doc_id] = sqrt(s) if s > 0.0 else 0.0
    return norms


def build_inverted_index(tfidf_vectors: dict[str, dict[str, float]]) -> dict[str, list[tuple[str, float]]]:
    index: dict[str, list[tuple[str, float]]] = {}
    for doc_id, vec in tfidf_vectors.items():
        for term, weight in vec.items():
            postings = index.setdefault(term, [])
            postings.append((doc_id, weight))
    for term, postings in index.items():
        postings.sort(key=lambda x: x[1], reverse=True)
    return index


def compute_query_vector(query_tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = compute_tf(query_tokens)
    return {term: tf_val * idf.get(term, 0.0) for term, tf_val in tf.items() if term in idf}


def rank_documents(
    query_tokens: list[str],
    index: dict[str, list[tuple[str, float]]],
    idf: dict[str, float],
    doc_norms: dict[str, float],
    top_k: int = 10,
) -> list[tuple[str, float]]:
    from collections import defaultdict

    query_vec = compute_query_vector(query_tokens, idf)
    if not query_vec:
        return []
    query_norm = sqrt(sum(weight * weight for weight in query_vec.values()))
    if query_norm == 0.0:
        return []
    scores: dict[str, float] = defaultdict(float)
    for term, q_weight in query_vec.items():
        postings = index.get(term, [])
        for doc_id, d_weight in postings:
            scores[doc_id] += q_weight * d_weight
    results: list[tuple[str, float]] = []
    for doc_id, dot in scores.items():
        norm = doc_norms.get(doc_id, 0.0)
        if norm > 0.0:
            score = dot / (norm * query_norm)
            results.append((doc_id, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
