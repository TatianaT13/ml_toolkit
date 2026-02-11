"""
VirusTotal API Integration
"""
import vt
import hashlib
import time
from typing import Dict, Optional

class VirusTotalIntegration:
    """Intégration avec VirusTotal pour validation croisée"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Clé API VirusTotal (gratuite sur virustotal.com)
        """
        self.client = vt.Client(api_key)
    
    def scan_file(self, filepath: str) -> Dict:
        """
        Scanner un fichier avec VirusTotal
        
        Args:
            filepath: Chemin vers le fichier
            
        Returns:
            Résultats du scan
        """
        # Calculer le hash
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        try:
            # Vérifier si déjà scanné
            file_report = self.client.get_object(f"/files/{file_hash}")
            
            return {
                'hash': file_hash,
                'detected': file_report.last_analysis_stats['malicious'] > 0,
                'detections': file_report.last_analysis_stats['malicious'],
                'total_engines': file_report.last_analysis_stats['malicious'] + 
                                file_report.last_analysis_stats['undetected'],
                'scan_date': file_report.last_analysis_date,
                'permalink': f"https://www.virustotal.com/gui/file/{file_hash}"
            }
        
        except vt.APIError as e:
            if e.code == 'NotFoundError':
                # Fichier pas encore scanné, l'uploader
                with open(filepath, 'rb') as f:
                    analysis = self.client.scan_file(f)
                
                # Attendre les résultats (peut prendre du temps)
                print("⏳ Scan en cours sur VirusTotal...")
                time.sleep(30)  # Attendre 30 secondes
                
                try:
                    file_report = self.client.get_object(f"/files/{file_hash}")
                    return {
                        'hash': file_hash,
                        'detected': file_report.last_analysis_stats['malicious'] > 0,
                        'detections': file_report.last_analysis_stats['malicious'],
                        'total_engines': file_report.last_analysis_stats['malicious'] + 
                                        file_report.last_analysis_stats['undetected'],
                        'scan_date': 'just now',
                        'permalink': f"https://www.virustotal.com/gui/file/{file_hash}"
                    }
                except:
                    return {'error': 'Scan in progress, try again in 1 minute'}
            else:
                return {'error': str(e)}
    
    def compare_with_ml_prediction(self, filepath: str, ml_prediction: int) -> Dict:
        """
        Compare prédiction ML avec VirusTotal
        
        Args:
            filepath: Chemin fichier
            ml_prediction: 0 (benign) ou 1 (malware)
            
        Returns:
            Comparaison détaillée
        """
        vt_result = self.scan_file(filepath)
        
        if 'error' in vt_result:
            return vt_result
        
        agreement = (ml_prediction == 1) == vt_result['detected']
        
        return {
            'ml_prediction': 'Malware' if ml_prediction == 1 else 'Benign',
            'vt_detected': vt_result['detected'],
            'vt_detections': f"{vt_result['detections']}/{vt_result['total_engines']}",
            'agreement': '✅' if agreement else '❌',
            'confidence': 'High' if agreement else 'Review needed',
            'vt_link': vt_result['permalink']
        }
    
    def close(self):
        """Fermer la connexion"""
        self.client.close()


# Exemple d'utilisation
if __name__ == "__main__":
    print("VirusTotal Integration Example")
    print("\n⚠️  You need a VirusTotal API key")
    print("Get one free at: https://www.virustotal.com/gui/join-us")
    print("\nUsage:")
    print("  vt = VirusTotalIntegration(api_key='YOUR_KEY')")
    print("  result = vt.scan_file('suspicious_file.exe')")
    print("  comparison = vt.compare_with_ml_prediction('file.exe', ml_prediction=1)")
