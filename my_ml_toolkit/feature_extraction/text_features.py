"""
Module d'extraction de features pour données textuelles
"""

import re
import numpy as np
from collections import Counter
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


class TextFeatureExtractor:
    """Extrait des features de données textuelles"""
    
    def __init__(self, max_features: int = 1000, ngram_range: tuple = (1, 2)):
        """
        Args:
            max_features: Nombre max de features pour TF-IDF
            ngram_range: Range de n-grams (1,1) = unigrams, (1,2) = uni+bigrams
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.tfidf_vectorizer = None
        self.count_vectorizer = None
    
    def extract_basic_features(self, text: str) -> Dict:
        """Features de base du texte"""
        words = text.split()
        
        features = {
            'text_length': len(text),
            'word_count': len(words),
            'char_count': len(text),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'digit_ratio': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
            'special_char_ratio': sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0,
        }
        
        return features
    
    def extract_statistical_features(self, text: str) -> Dict:
        """Features statistiques"""
        words = text.split()
        
        if not words:
            return {}
        
        word_lengths = [len(w) for w in words]
        
        features = {
            'unique_words': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words),
            'max_word_length': max(word_lengths),
            'min_word_length': min(word_lengths),
            'std_word_length': np.std(word_lengths),
        }
        
        return features
    
    def fit_tfidf(self, texts: List[str]):
        """Entraîne le vectoriseur TF-IDF"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range
        )
        self.tfidf_vectorizer.fit(texts)
    
    def transform_tfidf(self, texts: List[str]) -> np.ndarray:
        """Transforme textes en vecteurs TF-IDF"""
        if self.tfidf_vectorizer is None:
            raise ValueError("Appelez fit_tfidf() d'abord")
        return self.tfidf_vectorizer.transform(texts).toarray()
    
    def extract_all_features(self, text: str) -> Dict:
        """Extrait toutes les features d'un texte"""
        features = {}
        features.update(self.extract_basic_features(text))
        features.update(self.extract_statistical_features(text))
        return features


if __name__ == "__main__":
    # Test
    extractor = TextFeatureExtractor()
    sample = "Ceci est un exemple de texte pour tester l'extraction de features."
    features = extractor.extract_all_features(sample)
    
    print("Features textuelles:")
    for key, value in features.items():
        print(f"  {key}: {value}")
