# English Style Guide: Remove AI Writing Patterns

Rules to keep English posts sounding human, not AI-generated. Apply when writing or editing English content.
Source: [blader/humanizer](https://github.com/blader/humanizer) (MIT), based on Wikipedia's "Signs of AI writing" (WikiProject AI Cleanup). Distilled for this blog.

> Korean posts follow [style-korean.md](./style-korean.md).

## Core rule

**Rewrite, don't delete. Preserve coverage.** If the original has five paragraphs, the rewrite has five. Keep meaning and facts (names, numbers, dates, quotes) exact. Match the intended voice.

## Content patterns to remove

1. **Significance inflation.** Watch: *stands/serves as, a testament to, plays a vital/pivotal/crucial role, underscores its importance, reflects broader, marks a shift, evolving landscape, indelible mark, deeply rooted.* → State the plain fact. ("marking a pivotal moment in the evolution of…" → just say what happened.)
2. **Notability puffery.** Watch: *cited in major outlets, active social media presence, leading expert.* → Replace with one concrete, sourced fact.
3. **Superficial "-ing" tails.** Watch: *highlighting…, ensuring…, reflecting…, showcasing…, fostering….* → Cut the fake-depth participle; make it a plain statement.
4. **Promotional language.** Watch: *boasts, vibrant, rich, profound, nestled, in the heart of, breathtaking, must-visit, renowned, groundbreaking, stunning.* → Neutral, factual tone.
5. **Vague attributions / weasel words.** Watch: *experts argue, observers have cited, industry reports, some critics say.* → Name the specific source or cut it.
6. **Em dash and en dash: don't use them.** The em dash (—) and en dash (–) read as AI. Do not use either in prose. Replace with a comma, a period (split the sentence), parentheses, or a colon. Avoid "—" as a list-item separator too; use a colon or restructure the item instead (e.g. "Langfuse: the open-source self-hosting favorite").
7. **No rhetorical-question headings.** Section headings phrased as questions ("What problem does it solve?", "How is it different?", "Why does this matter?") read as AI or listicle filler. Use plain declarative noun headings instead: "The problem", "How it differs", "Why it matters". Better yet, a concrete noun phrase specific to the content. Keep headings short and factual. If a heading ends in "?", treat it as a warning sign.
8. **Rule of three.** AI loves triads ("fast, reliable, and scalable"). Break the reflex: use one or two, or a different structure.
9. **Negative parallelism.** "It's not just X, it's Y" / "This isn't about X, it's about Y." Overused. Rewrite directly.
10. **AI vocabulary.** *delve, leverage, robust, seamless, realm, tapestry, navigate the complexities, in today's fast-paced world, it's worth noting, crucial, pivotal.* Plain words instead.
11. **Filler / hedging.** "It's important to note that," "When it comes to," "In order to." Cut or simplify.
12. **Conclusion clichés.** "In conclusion," "Ultimately," "In summary." End on substance, not a pivot word.

## Voice (apply to blog posts/opinion, not to neutral reference text)

Clean-but-soulless is just as obvious as slop. For blog posts:

- **Have an opinion.** React, don't just report. "I'm not sure this holds up in production" beats a neutral pros/cons list.
- **Vary rhythm.** Short, punchy sentences. Then a longer one that takes its time. Mixed.
- **Let some mess in.** Asides and half-formed thoughts read human; perfect uniform structure reads algorithmic.

> For purely technical/reference passages (specs, API), neutral and plain *is* the correct human voice. Don't force opinions or first person there.

## Self-check after writing

1. Names, numbers, dates, quotes preserved exactly.
2. Coverage matches the original (no dropped points).
3. No em dashes or en dashes, no rhetorical-question headings, no triads, no "not just X but Y" reflexes.
4. Vocabulary is plain; no *delve/leverage/robust/tapestry*.
5. Voice fits the genre (opinion has a pulse; reference stays neutral).
