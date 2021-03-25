import requests
import winsound
import time

from datetime import datetime


URL_FORMAT = r'https://www.gov.il/BlobFolder/reports/daily-report-{date}/he/daily-report_daily-report-{date}.pdf'


def beep():
    frequency = 500
    duration = 200  # ms
    for _ in range(3):
        winsound.Beep(frequency, duration)


def main():
    url = URL_FORMAT.format(date=datetime.now().strftime('%Y%m%d'))
    print(f"Polling for {url}")
    while True:
        try:
            status = requests.get(url).status_code
            now = datetime.now().strftime('%H:%M:%S')
            print(f'{now}: {status}')
            if status == 200:
                break
        except Exception:
            pass
        time.sleep(30)
    beep()


if __name__ == '__main__':
    main()
