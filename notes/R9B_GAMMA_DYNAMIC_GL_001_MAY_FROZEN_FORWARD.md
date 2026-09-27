# Gamma Dynamic GL 001 — May frozen forward

Status: VERIFIED_DURABLE_FROZEN_FORWARD. August sealed.

Original January-trained ownership router applied unchanged to May.

Parent: 25,525 trades / 17,412 winners / -$4,425.2955 net / -$9,751.7455 GL / DD $4,425.6450.
Candidate: 22,034 trades / 15,334 winners / -$3,606.2150 net / -$8,361.6010 GL / DD $3,607.2835.
Delta: 14.2553% GL reduction; 88.0657% winner retention; 86.3232% trade retention; +$819.0805 net; 18.4913% DD reduction.

The frozen ownership effect strengthens in May versus April. No retuning, no May fitting, no failure-layer/path augmentation.

A pre-sync engineering run exposed one nonfinite parent outcome because the GL cache builder had marked every cached parent event as closed. The invalid run was not persisted scientifically. Builder was corrected to set parent closed-state from finite cached outcome; rerun then reproduced the authoritative May parent exactly at 25,525 trades and -$4,425.2955 net.

Result SHA256 22dbffa2e7a7d2117ab70f56bc6b6daa73731cd0811052c013e3e774bbd64d69.
Source SHA256 94538cd852d2afd87392ffded58b5bd2b3c50fb4a80139bedd62c03b146351c5.
