import os
import ssl
import yt_dlp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import subprocess

# Ignorar a verificação de certificado SSL (não recomendado)
ssl._create_default_https_context = ssl._create_unverified_context


# Substituir a função ffmpeg_extract_subclip para incluir o parâmetro -strict -2
def custom_ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """
    Usando uma função personalizada para extrair subclipes com ffmpeg,
    incluindo o parâmetro -strict -2.
    """
    if not targetname:
        targetname = filename
    cmd = [
        "ffmpeg",
        "-y",  # Sobrescreve o arquivo se ele já existir
        "-i", filename,
        "-ss", str(t1),
        "-to", str(t2),
        "-c", "copy",  # Copia o codec de vídeo e áudio sem recodificação
        "-strict", "-2",  # Permite o uso de Opus em MP4
        targetname
    ]
    subprocess.run(cmd, check=True)

# Função para baixar o vídeo e áudio na melhor qualidade
def download_video(url, output_path='video.mp4'):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Baixa o melhor vídeo e áudio separadamente, e os mescla
        'outtmpl': output_path,
        'merge_output_format': 'mp4',  # Garante que o formato final seja MP4
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Converte para MP4 se necessário
        }],
        'keepvideo': True,  # Não deleta o vídeo original após a mesclagem
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Tenta extrair e baixar o vídeo com a melhor qualidade
            info = ydl.extract_info(url, download=True)
            video_length = info['duration']  # Obtém a duração do vídeo
        except yt_dlp.utils.ExtractorError as e:
            print(f"Erro ao baixar o vídeo: {str(e)}")
            video_length = 0
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
        custom_ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_filename)
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
