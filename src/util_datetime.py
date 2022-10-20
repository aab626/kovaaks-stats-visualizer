import datetime

def avg_datetime(timestamps_list):
	timestamps = [dt.timestamp() for dt in timestamps_list]
	return datetime.datetime.fromtimestamp(sum(timestamps)/len(timestamps))
