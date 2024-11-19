import os
import re
import pytube
import yt_dlp
import requests
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip

def sanitize_filename(filename):
    """Nettoie le nom de fichier pour éviter les erreurs."""
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def download_youtube_video(url, output_path, with_watermark=False):
    """Télécharge une vidéo YouTube."""
    try:
        yt = pytube.YouTube(url)
        video = yt.streams.get_highest_resolution()
        
        filename = sanitize_filename(yt.title)
        video_path = video.download(output_path=output_path, filename=f"{filename}.mp4")
        
        if with_watermark:
            add_watermark(video_path, "YouTube")
        
        return filename, video_path
    except Exception as e:
        print(f"Erreur YouTube: {e}")
        return None, None

def download_tiktok_video(url, output_path, with_watermark=False):
    """Télécharge une vidéo TikTok."""
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'mp4'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = sanitize_filename(info_dict.get('title', 'tiktok_video'))
            video_path = ydl.prepare_filename(info_dict)
        
        if with_watermark:
            add_watermark(video_path, "TikTok")
        
        return filename, video_path
    except Exception as e:
        print(f"Erreur TikTok: {e}")
        return None, None

def add_watermark(video_path, platform):
    """Ajoute un filigrane à la vidéo."""
    try:
        clip = VideoFileClip(video_path)
        
        watermark = TextClip(
            platform, 
            fontsize=50, 
            color='white', 
            font='Arial-Bold'
        ).set_position(('center', 'bottom')).set_duration(clip.duration)
        
        final_clip = CompositeVideoClip([clip, watermark.set_opacity(0.5)])
        final_clip.write_videofile(video_path.replace('.mp4', '_watermarked.mp4'))
        
        clip.close()
        final_clip.close()
    except Exception as e:
        print(f"Erreur filigrane: {e}")