# AWS SAA-C03 Visual Course

To-the-point, visual study course for the **AWS Certified Solutions Architect – Associate (SAA-C03)** exam.

Open the site, work lesson by lesson, and practice architecture decisions — not glossary memorization.

## Quick start

**On GitHub Pages** (after Pages is enabled on this repo):

`https://pragasennaicker.github.io/SAA-C03-prep/`

**Locally:**

```bash
# from the repo root
python3 -m http.server 8000
# then open http://localhost:8000
```

Or open `index.html` directly in a browser (progress still saves via `localStorage`).

## How to study

For each lesson:

1. **Draw** the visual model from memory.
2. **Trace** the request/data path and the control that permits or blocks it.
3. **Stress** AZ and Region failure modes (and RPO/RTO where relevant).
4. **Decide** using the decision table and exam-language decoder.
5. **Check** yourself with the five scenario questions.

Mark a lesson complete when you can explain the path, failure mode, scaling mechanism, and cost trade-off without notes.

## Course map

| # | Lesson |
|---|--------|
| 01 | Networking Foundations |
| 02 | Connecting Networks & Global Routing |
| 03 | EC2, Load Balancing & Auto Scaling |
| 04 | Storage Architecture |
| 05 | Databases & Caching |
| 06 | IAM, Organizations & Authorization |
| 07 | Application Security & Data Protection |
| 08 | Serverless, APIs & Front Ends |
| 09 | Containers & Compute Choices |
| 10 | Messaging, Integration & Event-Driven Design |
| 11 | Resilience, Backup & Disaster Recovery |
| 12 | Edge, Global Performance & DNS |
| 13 | Data, Analytics & Streaming |
| 14 | Migration, Transfer & Hybrid Storage |
| 15 | Monitoring, Governance & Operations |
| 16 | Cost Optimization & Architecture Trade-offs |
| 17 | Final Architecture Patterns & Exam Strategy |

Domain weighting on the exam: **Security 30% · Resilience 26% · Performance 24% · Cost 20%**.

## Repo layout

```text
index.html                 # course hub
lessons/                   # one HTML page per lesson
appendix/service-atlas.html
assets/css/course.css
assets/js/course.js
```

## GitHub Pages

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/ (root)`
4. Save — site will publish at `https://<user>.github.io/SAA-C03-prep/`

## Disclaimer

Unofficial study aid. **Not affiliated with Amazon Web Services.** Always verify details against the current [SAA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html) and AWS documentation. Service scope and exam emphasis can change.

## License

MIT — see [LICENSE](LICENSE).
