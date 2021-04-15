from encoder import UniversalEncoder

encoder = UniversalEncoder("tstsv.ddns.net", 8501)
r = encoder.search("day by day",1)
[print(i) for i in r]
