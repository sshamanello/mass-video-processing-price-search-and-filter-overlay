import os
import subprocess

def combine_audio_video(audio_dir, video_dir, output_dir):
    # Создаем выходную директорию, если она не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Получаем списки всех аудио- и видеофайлов в соответствующих директориях
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.aac')])
    video_files = sorted([f for f in os.listdir(video_dir) if f.endswith('.mp4')])

    # Проверяем, что количество аудио- и видеофайлов совпадает
    if len(audio_files) != len(video_files):
        print(f'Количество аудио- и видеофайлов не совпадает: {len(audio_files)} аудио, {len(video_files)} видео.')
        return

    # Обходим каждый аудиофайл и соответствующий ему видеофайл
    for audio_file, video_file in zip(audio_files, video_files):
        # Формируем пути к аудио- и видеофайлам
        audio_path = os.path.join(audio_dir, audio_file)
        video_path = os.path.join(video_dir, video_file)

        # Формируем путь к выходному файлу
        output_file_base = os.path.splitext(video_file)[0]
        output_file = f"{output_file_base}_final.mp4"
        output_path = os.path.join(output_dir, output_file)

        # Команда ffmpeg для объединения видео и аудио
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            output_path
        ]

        # Выполняем команду ffmpeg
        try:
            subprocess.run(command, check=True)
            print(f'Файл {output_file} успешно создан.')
        except subprocess.CalledProcessError as e:
            print(f'Ошибка при обработке файла {audio_file} и {video_file}: {e}')



# Указываем пути к папкам с аудио и видеофайлами и папке для сохранения результата
audio_directory = r'C:/Users/ngrin/Desktop/work/WB/тесты/output_audio'
video_directory = r'C:/Users/ngrin/Desktop/work/WB/тесты/output_videos'
output_directory = r'C:/Users/ngrin/Desktop/work/WB/тесты/combined_videos'

# Вызываем функцию для соединения аудио и видеофайлов
combine_audio_video(audio_directory, video_directory, output_directory)
