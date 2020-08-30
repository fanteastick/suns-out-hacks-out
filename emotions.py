import heapq

# possible emotions: anger, contempt, disgust, fear, happiness,
#                    neutral, sadness, surprise
emotion_mapping = {'anger': 0,
                   'contempt': 1,
                   'disgust': 2,
                   'fear': 3,
                   'happiness': 4,
                   'neutral': 5,
                   'sadness': 6,
                   'surprise': 7}

class FilterEmotions:
    def __init__(self, emotions):
        # Stores scores as (score, emotion name), top is max
        self.emotions = [(-emotions.__dict__[key], key) for key in emotions.__dict__ if type(emotions.__dict__[key]) == float]
        heapq.heapify(self.emotions)
            
    def get_top_emotions(self, n):
        # Returns emotions as sorted list of (score, emotion name)
        return heapq.nsmallest(n, self.emotions)
    
    def get_top_emotion_name(self):
        return self.emotions[0][1]
    
    def get_top_emotion_score(self):
        return -self.emotions[0][0]
