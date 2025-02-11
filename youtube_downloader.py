import yt_dlp
import os
import subprocess
import json

def get_audio_streams(file_path):
    """
    Obtém as faixas de áudio disponíveis no arquivo utilizando o ffprobe.
    """
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'a',
        '-print_format', 'json',
        '-show_streams',
        '-probesize', '50M',  # Aumenta o tamanho da análise
        '-analyzeduration', '100M',  # Aumenta o tempo de análise
        file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        streams = json.loads(result.stdout).get("streams", [])
        return streams
    except Exception as e:
        print("Erro ao obter faixas de áudio:", e)
        return []

def select_audio_track(file_path):
    """
    Se houver mais de uma faixa de áudio, permite ao usuário escolher qual deseja manter.
    Em seguida, utiliza o ffmpeg para criar um novo arquivo contendo apenas a faixa selecionada.
    """
    streams = get_audio_streams(file_path)
    if len(streams) <= 1:
        print("Não há mais de uma faixa de áudio disponível para seleção.")
        return

    print("\nFaixas de áudio disponíveis:")
    for idx, stream in enumerate(streams):
        desc = f"{idx}: Codec: {stream.get('codec_name', 'desconhecido')}"
        tags = stream.get('tags', {})
        language = tags.get('language', 'indefinido')
        desc += f", Linguagem: {language}"
        channels = stream.get('channels')
        if channels:
            desc += f", Canais: {channels}"
        print(desc)

    choice = input("Digite o número da faixa de áudio que deseja manter (ou pressione Enter para manter todas): ")
    if choice.strip() == "":
        print("Mantendo todas as faixas de áudio.")
        return
    try:
        choice_int = int(choice)
        if not (0 <= choice_int < len(streams)):
            print("Opção inválida. Mantendo todas as faixas de áudio.")
            return
    except ValueError:
        print("Valor inválido. Mantendo todas as faixas de áudio.")
        return

    selected_stream = streams[choice_int]
    selected_stream_index = selected_stream.get('index')
    print(f"Selecionada faixa de áudio com índice {selected_stream_index}.")

    # Define o nome do arquivo de saída (adicionando o sufixo _selected antes da extensão).
    base, ext = os.path.splitext(file_path)
    output_file = base + "_selected" + ext

    # Comando ffmpeg para manter todos os streams de vídeo e somente a faixa de áudio escolhida.
    cmd = [
        'ffmpeg', '-y',
        '-i', file_path,
        '-map', '0:v',
        '-map', f'0:{selected_stream_index}',
        '-c', 'copy',
        output_file
    ]
    print("Reprocessando o arquivo para manter apenas a faixa de áudio selecionada...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"Processamento concluído com sucesso! Arquivo resultante: {output_file}")
        # Caso queira remover o arquivo original após o processamento, descomente a linha abaixo:
        # os.remove(file_path)
    else:
        print("Erro durante o processamento com ffmpeg:")
        print(result.stderr)

def download_video(url):
    """
    Faz o download do vídeo utilizando o yt_dlp e, após a conclusão, verifica as faixas de áudio
    disponíveis permitindo a escolha, se houver mais de uma.
    """
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        # Primeiro, extrair informações sem fazer download
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'no_warnings': True,
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            
        # Mostrar formatos de áudio disponíveis
        print("\nFaixas de áudio disponíveis:")
        audio_tracks = []
        for f in info.get('formats', []):
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                language = f.get('language') or 'indefinido'
                print(f"ID: {f['format_id']}, Linguagem: {language}, Formato: {f['ext']}")
                audio_tracks.append(f)

        # Permitir escolha do áudio
        chosen_audio = None
        if len(audio_tracks) > 1:
            choice = input("\nEscolha o ID da faixa de áudio desejada (Enter para padrão): ").strip()
            if choice:
                chosen_audio = next((t for t in audio_tracks if t['format_id'] == choice), None)

        # Configurações para o download
        ydl_opts = {
            'format': f'bv*[height<=720]+{chosen_audio["format_id"] if chosen_audio else "ba"}',
            'progress_hooks': [lambda d: print(f'\rBaixando: {d["_percent_str"]}', end='')],
            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'keepvideo': False,
            'writethumbnail': False,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'http_headers': {
                'Accept-Language': 'pt-BR,pt;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            },
            'postprocessor_args': [
                '-map', '0:v:0?',
                '-map', '0:a:0?',
                '-c:v', 'copy',
                '-c:a', 'aac',
            ],
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

if __name__ == "__main__":
    url = input("Digite a URL do vídeo do YouTube: ")
    download_video(url)