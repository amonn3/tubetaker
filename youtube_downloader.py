import yt_dlp
import os

def download_video(url):
    try:
        # Obtém o caminho da pasta Downloads
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        # Configurações do yt-dlp
        ydl_opts = {
            # Seleciona formato MP4 em 720p com áudio
            'format': 'bv*[ext=mp4][height=720]+ba[ext=m4a]/b[ext=mp4][height<=720]/bv*+ba/b',
            'progress_hooks': [lambda d: print(f'\rBaixando: {d["_percent_str"]}', end='')],
            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            # Limpa arquivos temporários após o download
            'keepvideo': False,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        print(f"\nIniciando download de: {url}")
        print(f"O vídeo será salvo em: {downloads_path}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        print("\nDownload completo!")
        
    except Exception as e:
        print(f'\nOcorreu um erro: {str(e)}')

url = input("Digite a URL do vídeo do YouTube: ")
download_video(url)