import os
import ssl
import yt_dlp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Ignorar a verificação de certificado SSL (não recomendado)
ssl._create_default_https_context = ssl._create_unverified_context

# Função para baixar o vídeo do YouTube
def download_video(url, output_path='video.mp4'):
    ydl_opts = {
        'format': 'best',  # Inicialmente tenta o melhor formato
        'outtmpl': output_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Tenta extrair e baixar o vídeo com o formato 'best'
            info = ydl.extract_info(url, download=True)
            video_length = info['duration']  # Obtém a duração do vídeo
        except yt_dlp.utils.ExtractorError as e:
            print(f"Erro ao baixar o formato 'best': {str(e)}")
            print("Listando formatos disponíveis...")
            
            # Extrai a lista de formatos disponíveis sem baixar
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Exibe os formatos disponíveis
            for f in formats:
                print(f'Format ID: {f["format_id"]}, Extension: {f["ext"]}, Resolution: {f.get("resolution", "N/A")}')
            
            # Escolhe um formato específico manualmente (por exemplo, ID 18, que é mp4 de baixa qualidade)
            format_id = input("Digite o Format ID desejado para baixar: ")
            ydl_opts['format'] = format_id
            
            # Tenta baixar com o formato escolhido
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                info = ydl_retry.extract_info(url, download=True)
                video_length = info['duration']  # Obtém a duração do vídeo
    return output_path, video_length  # Retorna o caminho do arquivo e a duração do vídeo em segundos

# Função para cortar o vídeo em partes de até 25 minutos
def split_video(video_path, video_length, part_duration=25*60, output_folder='parts'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    parts = video_length // part_duration  # Número de partes completas
    remaining = video_length % part_duration  # Tempo restante para a última parte
    
    start_time = 0
    part_number = 1

    # Cortar as partes de 25 minutos
    while start_time < video_length:
        end_time = min(start_time + part_duration, video_length)
        output_filename = os.path.join(output_folder, f"part_{part_number}.mp4")
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_filename)
        print(f"Criado: {output_filename} (de {start_time} até {end_time} segundos)")
        
        start_time += part_duration
        part_number += 1

    print(f"Vídeo dividido em {part_number - 1} partes.")

# Função principal
def main(url):
    video_path, video_length = download_video(url)
    split_video(video_path, video_length)

# Exemplo de uso
if __name__ == "__main__":
    youtube_url = input("Digite a URL do vídeo do YouTube: ")
    main(youtube_url)
