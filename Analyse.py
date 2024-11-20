import re
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
from bidi.algorithm import get_display
import os

class Analyse:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, "r") as file:
            self.text = file.read()
            self.lines = self.text.split("\n")
        self.data = {}
        self.get_messages()

    def get_messages(self):
        pattern = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} - '

        messages = re.split(pattern, self.text)

        time_stamps = []
        for msg in self.lines:
            match = re.match(r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} - ', msg)
            if match:
                datetime_str = match.group()
                datetime_str_ = datetime_str.split(", ")
                time_stamps.append((datetime_str_[0], datetime_str_[1].removesuffix(" - ")))

        messages.pop(0)

        for msg, time in zip(messages, time_stamps):
            msg = msg.removesuffix("\n")
            if ":" not in msg:
                continue
            name = msg.split(":")[0]
            content = msg.removeprefix(name + ": ")
            date = time[0]
            time_hour = time[1]
            if name not in self.data.keys():
                self.data[name] = []
            self.data[name].append((date, time_hour, content))

    def print_names(self):
        for name in self.data:
            print(name)

    def count_word(self, word, capital=False, name=None):
        count = 0
        if name:
            if not capital:
                word = word.lower()
            for message in self.data[name]:
                if capital:
                    count += message[2].count(word)
                else:
                    count += message[2].lower().count(word)
            return count
        if capital:

            for name in self.data:
                for message in self.data[name]:
                    count += message[2].count(word)
            return count
        for name in self.data:
            word = word.lower()
            for message in self.data[name]:
                count += message[2].lower().count(word)
        return count

    def get_message_count(self, name=None):
        if name:
            return len(self.data[name])
        messages = 0
        for name in self.data:
            messages += len(self.data[name])
        return messages

    def get_leaderboards(self):
        leaderboards = {}
        for name in self.data:
            leaderboards[name] = self.get_message_count(name)

        sorted_leaderboards = self.sort_dict(leaderboards)
        return sorted_leaderboards

    def get_leaderboards_formated(self):
        sorted_leaderboards = self.get_leaderboards()
        leaderboards = []
        for i, x in enumerate(sorted_leaderboards):
            name, count = x
            leaderboards.append(f"{i + 1}. {name} - {count} messages")
        return "\n".join(leaderboards)

    def get_words_dict(self, name=None):
        words = {}
        names = self.data
        if name:
            names = [name]
        for name in names:
            for message in self.data[name]:
                for word in message[2].split(" "):
                    word = word.strip(".,!?*()[]{}\"\'")
                    if word not in words.keys():
                        words[word] = 0
                    words[word] += 1
        return words

    def get_word_leaderboards(self, word, capital=False):
        leaderboards = {}
        for name in self.data:
            leaderboards[name] = self.count_word(word, capital, name)
        return self.sort_dict(leaderboards)

    def get_list_leaderboards(self, words, capital=False, do_sum=True):
        leaderboards = {}
        for name in self.data:
            leaderboards[name] = []
            for word in words:
                leaderboards[name].append(self.count_word(word, capital, name))
        sorted_list = self.sort_dict(leaderboards, True)
        if do_sum:
            for i in range(len(sorted_list)):
                sorted_list[i].append(sum(sorted_list[i][1:]))
        print(sorted_list)
        return sorted_list

    def get_message_times(self, name=None):
        names = self.data.keys()
        if name:
            names = [name]
        times = []
        for name in names:
            for message in self.data[name]:
                times.append(message[1])
        return times

    def get_message_count_in_interval(self, start, end, name=None):
        count = 0
        times = self.get_message_times(name)
        for time in times:
            if self.is_in_time_interval(time, start, end):
                count += 1
        return count

    def get_leaderboards_in_interval(self, start, end):
        leaderboards = {}
        for name in self.data:
            leaderboards[name] = self.get_message_count_in_interval(start, end, name)
        sorted_leaderboards = self.sort_dict(leaderboards)
        return sorted_leaderboards

    @staticmethod
    def sort_dict(dict, unpack=False):
        l = list(sorted(dict.items(), key=lambda item: item[1], reverse=True))
        if not unpack:
            return l
        if unpack:
            l_unpacked = []
            for i in range(len(l)):
                l_unpacked.append([])
                l_unpacked[i].append(l[i][0])
                for y in l[i][1]:
                    l_unpacked[i].append(y)

        return l_unpacked

    @staticmethod
    def create_table(headers, data, filename, show=False, title=None):
        """
        headers = ["Name", "Message Count"]
        data = [(name1, count1), (name2, count2]
        """
        table_data = {}
        for i, header in enumerate(headers):
            header = get_display(header)
            table_data[header] = [get_display(str(x[i])) for x in data]
        df = pd.DataFrame(table_data)
        rcParams['font.family'] = 'Arial'
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.axis('off')
        if not title:
            title = filename.removesuffix("." + filename.split('.')[-1])
        ax.set_title(title, fontsize=12, fontweight="bold", pad=50)
        table = ax.table(cellText=df.values,
                         colLabels=df.columns,
                         loc='center',
                         cellLoc='center',
                         colColours=["#a1d0ff"] * len(df.columns))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)
        table.auto_set_column_width(col=list(range(len(df.columns))))
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        if show:
            os.startfile(filename)

    @staticmethod
    def average_time(list_of_times):
        times = 0
        for time in list_of_times:
            time = int(time.split(":")[0])*60 + int(time.split(":")[1])
            times += time
        avg = times/len(list_of_times)
        hour, minute = divmod(avg, 60)
        return f"{int(hour):02}:{int(minute):02}"

    @staticmethod
    def frequent_time(data):
        times = set(data)
        time_frequency = {}
        for time in times:
            time_frequency[time] = data.count(time)
        return Analyse.sort_dict(time_frequency)

    @staticmethod
    def is_in_time_interval(time, start, end):
        time = int(time.split(":")[0])*60 + int(time.split(":")[1])
        start = int(start.split(":")[0])*60 + int(start.split(":")[1])
        end = int(end.split(":")[0])*60 + int(end.split(":")[1])
        if start > end:
            return start <= time or time <= end
        return start <= time <= end
