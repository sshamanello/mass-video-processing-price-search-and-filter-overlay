import os
import ffmpeg
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

# Путь к файлу шрифта
FONT_FILE = "rockwellmt.otf"

def detect_scene_changes(video_path):
    try:
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        video_manager.set_downscale_factor()
        video_manager.start()

        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        video_manager.release()

        print(f"Обнаружено {len(scene_list)} сцен в видео {video_path}.")
        return scene_list
    except Exception as e:
        print(f"Ошибка при обнаружении сцен в видео {video_path}: {e}")
        return []

def extract_audio(video_path, output_audio_directory):
    try:
        audio_filename = os.path.splitext(os.path.basename(video_path))[0] + '.aac'
        output_audio_path = os.path.join(output_audio_directory, audio_filename)
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, acodec='aac')
            .run(overwrite_output=True)
        )
        print(f"Аудио успешно извлечено из видеоролика {video_path}.")
        return output_audio_path
    except ffmpeg.Error as e:
        print(f"Ошибка при извлечении аудио из видеоролика {video_path}: {e}")
        return None

def add_white_box_with_text(video_path, start_time, output_path, y_position, rectangle_height, font_size):
    try:
        # Получаем общую длительность видео
        probe = ffmpeg.probe(video_path)
        video_duration = float(probe['format']['duration'])

        # Накладываем белый прямоугольник и текст
        (
            ffmpeg
            .input(video_path)
            .filter('drawbox', x=0, y=y_position, w=probe['streams'][0]['width'], h=rectangle_height, color='white@1.0', t='fill', enable=f"between(t,{start_time},{video_duration})")
            .filter('drawtext', text='Артикулы в ТГ @wbfinds82', x='(w-text_w)/2', y=y_position + rectangle_height // 2 - (font_size // 2), fontsize=font_size, fontcolor='black', fontfile=FONT_FILE, enable=f"between(t,{start_time},{video_duration})")
            .output(output_path, vcodec='libx264', crf=23, pix_fmt='yuv420p', an=None)  # отключаем аудио
            .run(overwrite_output=True)
        )
        print(f"Белый прямоугольник и текст успешно наложены на видео {video_path} с {start_time} до конца ({video_duration}).")
    except ffmpeg.Error as e:
        print(f"Ошибка при наложении белого прямоугольника и текста на видео {video_path}: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка при обработке видео {video_path}: {e}")

def combine_audio_video(audio_directory, video_directory, output_directory):
    # Создание выходной директории, если она не существует
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Обход всех аудиофайлов в директории
    for audio_filename in os.listdir(audio_directory):
        if audio_filename.endswith('.aac'):
            audio_path = os.path.join(audio_directory, audio_filename)
            video_filename = os.path.splitext(audio_filename)[0] + '.mp4'
            video_path = os.path.join(video_directory, video_filename)
            output_filename = os.path.splitext(audio_filename)[0] + '_merged.mp4'
            output_path = os.path.join(output_directory, output_filename)

            # Проверка существования видеофайла
            if os.path.exists(video_path):
                # Объединение аудио и видео
                try:
                    ffmpeg.input(video_path).output(output_path, c='copy', map='0:v:0', map_audio='1:a:0').run(overwrite_output=True)
                    print(f"Файлы {audio_filename} и {video_filename} успешно объединены и сохранены как {output_filename}.")
                except ffmpeg.Error as e:
                    print(f"Ошибка при объединении файлов {audio_filename} и {video_filename}: {e}")
            else:
                print(f"Видеофайл {video_filename} не найден для аудиофайла {audio_filename}.")

def process_video(video_path, output_path, output_audio_directory, output_video_directory):
    # Извлечение аудио из видео
    audio_path = extract_audio(video_path, output_audio_directory)
    if audio_path:
        # Обработка видео
        scenes = detect_scene_changes(video_path)
        if len(scenes) > 1:
            # Начало после танцевального фрагмента - это конец первой сцены
            end_time = scenes[0][1].get_seconds()
            print(f"Для видео {video_path}: начало {end_time} сек для наложения белого прямоугольника и текста.")
            # Определяем высоту прямоугольника и размер шрифта
            probe = ffmpeg.probe(video_path)
            width = int(probe['streams'][0]['width'])
            height = int(probe['streams'][0]['height'])
            if width == 1080 and height == 1920:
                rectangle_height = 600
                font_size = 58
            elif width == 720 and height == 1280:
                rectangle_height = 300
                font_size = 36
            else:
                # По умолчанию, если разрешение не соответствует ожидаемым, используем высоту 500 и размер шрифта 48
                rectangle_height = 500
                font_size = 48
            # Определяем границы изображения
            y_position = 0  # чтобы прямоугольник был сверху
            print(f"Для видео {video_path}: верхняя граница {y_position}, высота {rectangle_height}.")
            
            # Добавление белого прямоугольника и текста к видео
            add_white_box_with_text(video_path, end_time, output_path, y_position, rectangle_height, font_size)
        else:
            print(f"Не удалось обнаружить сцены в видео {video_path}.")
        
        # Объединение аудио и видео
        combine_audio_video(output_audio_directory, output_video_directory, output_directory)
    else:
        print(f"Не удалось извлечь аудио из видеоролика {video_path}.")

def process_all_videos(input_directory, output_audio_directory, output_video_directory, output_directory):
    # Создание выходных директорий, если они не существуют
    for directory in [output_audio_directory, output_video_directory, output_directory]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Обход всех файлов во входной директории
    for filename in os.listdir(input_directory):
        # Проверка, является ли файл видеофайлом
        if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # Формирование путей к входному и выходному файлам
            input_path = os.path.join(input_directory, filename)
            output_name = os.path.splitext(filename)[0] + ' wb.finds82.mp4'
            output_path = os.path.join(output_video_directory, output_name)
            
            # Вывод логов о начале обработки файла
            print(f"Начинаю обработку файла: {output_name}")
            
            # Обработка видеофайла
            process_video(input_path, output_path, output_audio_directory, output_video_directory)
            
            # Проверка, был ли файл сохранен
            if os.path.exists(output_path):
                print(f"Файл {output_name} успешно обработан и сохранен в {output_path}.")
            else:
                print(f"Ошибка: файл {output_name} не был сохранен.")

# Пример использования
input_directory = 'C:/Users/ngrin/Desktop/work/WB/тесты'
output_audio_directory = 'C:/Users/ngrin/Desktop/work/WB/тесты/output_audio'
output_video_directory = 'C:/Users/ngrin/Desktop/work/WB/тесты/output_videos'
output_directory = 'C:/Users/ngrin/Desktop/work/WB/тесты/output'
process_all_videos(input_directory, output_audio_directory, output_video_directory, output_directory)
