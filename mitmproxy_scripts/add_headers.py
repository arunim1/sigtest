from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from mitmproxy import http
import time

with open("/certs/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

# private_key_str = """
# -----BEGIN PRIVATE KEY-----
# MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1hsRoC/9MSlrJ
# DilUcX69tKwIuWhh/yBD/8/W0itbV0hfZR6JnAUJd+3xUEd7vcAILHD2W9GK095t
# v4yCjulO+eOzVmt47ahHFIqC/ZyN+RAvQWYUf/rJn/M/K5JIlwJYloo9CPet/ISx
# a6PbzmXKyG8YopiUlFjFComi2iT05DepTU00eiP/+kJGOgXtPy7xIp3bSx69dhD5
# IJqOcNeYa6CTJ18hTi6UhmvlRyUB6oVwUaMLMOTo5YbmgVYLzyKx5SHgc6klXAH8
# SrxaSwYenMWyhPJu1G+1m4UROuwdYkNQGQhdSRTZjc4aBHKpO36vC+XQ1o0mngt9
# 8eG7DSWPAgMBAAECggEAApfom268ckvhP/Xk7xEC1TwAQmZy6gXmlJu4tCJJi0lt
# pJGoKrtUMrGIPTlySmX7sqiYro30qiD8kKEH2JLcUD88TdyCT/Z5QBa4VqzzFryQ
# 5Icj9oJp91J1+7H09sOHI/PdCSH+w9+tMTzov0p6F56rptrzBubKdxPMKcvBczXM
# G8rzyC+lM3gVCBN2wx7MjaV+koZNl27Q0wOebTe4Er/vRBoiozixFL4VnjvPcfh5
# nZ3RUrSTvp0lFLLgglE2n1LANWK2fSNICzXmCTXYOFPgCeAGjizr5Az7QDDf1pvh
# ogPLtfPJJ9A1VhCRdq259Yn90yYmj6vN0aGKoBXfgQKBgQDjliib2gsAzfybKMUp
# 71L2geJ8rbbmb6tvPIjcVTP0YTjH9wVZ9HWwwzHWV2AUEa9TxcrIe71FN8eSTd0C
# sX7w3Liuf6PMci6UELVMIG0ZVCRLI5dt1s2TDg+57pfkDi7kgBhcPLgWjeoQNGXH
# NA549/jG3+ntJZj49EWbg2NNDwKBgQDMMH3cYOgZuysmLubWFyRxLvULU6wxtGce
# rhACBVu0QE0d/jUDBuouTHyYh5QzCeZGSLdt1/YxpOXvD7LzhZbHrq8Umh0++rYd
# ibdiToPhbKKmGY9RTPPzYg0XghRozHtLe6VRHvtErFRh+0zwEo6mKlxTCxHVj3O6
# E/NY4mmfgQKBgFUmMTtecQ90AjbrIhl2eUvRfLO5Kt08mp+bvnjxR+b/GQd33ICz
# ffUMkvDm8AOSOk7VifFImp/zJrAOgcooLp5fdpmTF+2+Kr8rISnCWA9J8+pI/rcR
# zwheEnQ2WI3y4IiNhI++CAIoRpKZiBrn1yJbZLDDxfn8Pyel/QUaO2TxAoGAb1ZV
# mpAAnt8u9QAIAF7YERswpH94WhXrUJBKzD9NtKiHJD6Te1YO5TXxjl4HEhloxZQq
# 6KskZAdtFQBzbFPAVptKfipWnhuop8yLAQCc6pMI0RcIzaTvNBuX1eSo6kftRshh
# 6SzCh7yLum2DkzgbLkHU27cif1dcG+969lFmlIECgYEAmZ/1zeyntXEQg+RhswSE
# VZpwMc9f4eVKe2gEFPysJWdLMxVbreIo5Xw5S24YZn3N51+cG1nZBiAcyIkVrERC
# lg7/2WZk+Alxo1G0nBl9c53onAh8reEtsyxEqwCH3H4MmL2XVPRg9qi66IcLELBg
# M4hsvnDZSPebbLgdL7NUUQk=
# -----END PRIVATE KEY-----
# """

# private_key_str = private_key_str.strip()

# private_key = serialization.load_pem_private_key(private_key_str.encode(), password=None)

def sign(request_id):
    timestamp = str(int(time.time()))
    
    # Create and sign message
    message = f"{timestamp} | {request_id}"
    print(f"Signing message: {message}", flush=True)
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print(f"Signature: {signature.hex()}", flush=True)
    
    # Return headers instead of JSON
    return timestamp, signature.hex()

def request(flow: http.HTTPFlow) -> None:
    print(flow.request.pretty_url, flush=True)

    # Skip non-HTTPS traffic
    # if not flow.client_conn.ssl_established:
    #     return

    # Get request ID
    request_id = "12309"
    flow.request.headers["Agent-ID"] = request_id

    timestamp, signature = sign(request_id)

    # Add headers to the request
    flow.request.headers["Agent-Timestamp"] = timestamp
    flow.request.headers["Agent-Signature"] = signature
    print(flow.request.headers, flush=True)
