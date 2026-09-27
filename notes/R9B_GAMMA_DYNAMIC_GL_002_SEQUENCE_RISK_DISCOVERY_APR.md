# Gamma Dynamic GL 002 — Sequence-risk discovery + April calibration

Status: VERIFIED_DURABLE_DIAGNOSTIC_CALIBRATION. Not promoted. August sealed.

Parent: GL001 frozen-January ownership core.

Mechanism: targeted PRE-ENTRY veto on already-owned CONTINUE trades when ownership confidence is low and the 30-second action-relative sequence is adverse. No delayed confirmation, no backdating, no future inputs.

Discovery/validation:
- Jan+Feb discovery screen: 432 transparent variants.
- Eligibility gate: positive additional GL reduction and net improvement in both months with >=97% ownership-core winner retention.
- 30 variants passed.
- March validation: all 12 shortlisted robust variants survived the same gate.
- Discovery-selected family: confidence <=0.55, CONTINUE only, action-relative ret30 <= 0.00. Minimum Jan/Feb additional GL reduction = 2.1448%; minimum winner retention = 97.0040%. March: +1.6453% additional GL reduction, 97.9655% winner retention, +$64.889 net, DD -1.1212%.

April calibration:
Best numeric repeats the discovery rule exactly: conf<=0.55 / CONTINUE / ret30<=0.00. It adds 2.7267% GL reduction versus GL001, retains 97.2851% GL001 winners, +$124.4435 net, DD -3.0119%.
Robust knee: conf<=0.55 / CONTINUE / ret30<=-0.05. It adds 2.4921% GL reduction, retains 97.4400% winners, +$110.786 net, DD -2.6813%.

Decision: freeze the robust knee for May-Jul. This is a reconstructible 012-inspired targeted containment sleeve that avoids the rejected 018 confirmation tax and the rejected generic 3s failure exit.

Discovery result SHA256 4ef3434979ca4475b53df4812862ba1d2140e68e9a03638b74caa5901e2b2f96.
April result SHA256 4a6c4afc82daf12f7c0ae9ffaf4cbed9f0a1d552a1042d20446e393cdf48484b.
