from flask import Flask, render_template, request, send_file, jsonify
import os
import utils

app = Flask(__name__)

# Configuration des chemins de téléchargement
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR_WITH_WATERMARK = os.path.join(BASE_DIR, 'downloads', 'with_watermark')
DOWNLOAD_DIR_WITHOUT_WATERMARK = os.path.join(BASE_DIR, 'downloads', 'without_watermark')

# Créer les répertoires s'ils n'existent pas
os.makedirs(DOWNLOAD_DIR_WITH_WATERMARK, exist_ok=True)
os.makedirs(DOWNLOAD_DIR_WITHOUT_WATERMARK, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    watermark_option = request.form.get('watermark', 'without')
    
    # Déterminer le type de plateforme
    if 'youtube.com' in url:
        platform = 'youtube'
    elif 'tiktok.com' in url:
        platform = 'tiktok'
    else:
        return jsonify({
            'success': False, 
            'message': 'Plateforme non supportée'
        })
    
    # Choix du répertoire de téléchargement
    download_dir = DOWNLOAD_DIR_WITH_WATERMARK if watermark_option == 'with' else DOWNLOAD_DIR_WITHOUT_WATERMARK
    
    try:
        # Téléchargement selon la plateforme
        if platform == 'youtube':
            filename, video_path = utils.download_youtube_video(
                url, 
                download_dir, 
                with_watermark=(watermark_option == 'with')
            )
        else:  # TikTok
            filename, video_path = utils.download_tiktok_video(
                url, 
                download_dir, 
                with_watermark=(watermark_option == 'with')
            )
        
        if not filename or not video_path:
            return jsonify({
                'success': False, 
                'message': 'Impossible de télécharger la vidéo'
            })
        
        return jsonify({
            'success': True, 
            'filename': filename,
            'path': video_path
        })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': str(e)
        })

@app.route('/get_video/<path:filename>')
def get_video(filename):
    # Parcourir les deux répertoires pour trouver le fichier
    for directory in [DOWNLOAD_DIR_WITH_WATERMARK, DOWNLOAD_DIR_WITHOUT_WATERMARK]:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
    
    return "Fichier non trouvé", 404

if __name__ == '__main__':
    app.run(debug=True)