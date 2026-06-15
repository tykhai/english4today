import azure.cognitiveservices.speech as speechsdk
import json

def assess_pronunciation(audio_bytes, reference_text):
    """
    Gửi file âm thanh lên Azure để chấm điểm phát âm theo câu mẫu (reference_text)
    """
    # Khai báo thông tin cấu hình Azure (Lấy key miễn phí từ Microsoft Azure)
    speech_config = speechsdk.SpeechConfig(subscription="KEY_CỦA_BẠN", region="eastus")
    
    # Cấu hình nhận diện audio từ luồng dữ liệu byte (in-memory)
    pull_stream = speechsdk.audio.PullAudioInputStream() # Hoặc dùng file tạm push_stream
    # (Để đơn giản hóa, Azure hỗ trợ đọc trực tiếp từ cấu hình luồng hoặc ghi file tạm .wav)
    
    # Thiết lập cấu hình chấm điểm phát âm
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme # Chấm đến từng âm tiết
    )
    
    # Khởi tạo bộ nhận diện
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    pronunciation_config.apply_to(speech_recognizer)
    
    # Thực hiện nhận diện và phân tích
    result = speech_recognizer.recognize_once()
    
    # Bóc tách kết quả trả về dạng JSON từ Azure
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        assessment_result = json.loads(result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        return assessment_result
    else:
        return None