import streamlink
session = streamlink.streamlink()
session.set_option("http-verify", False)
streams = streamlink.streams('https://www.fox.com.tr/canli-yayin', session=session)
print(streams["best"].multivariant.uri)
