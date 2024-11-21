import re


def convert_date_format(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    def replace_date(match):
        day, month, year = match.groups()
        return f"{int(month)}/{int(day)}/{year[-2:]}"

    updated_content = re.sub(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', replace_date, content)

    with open(file_path, 'w') as file:
        file.write(updated_content)


if __name__ == '__main__':
    convert_date_format('data.txt')
