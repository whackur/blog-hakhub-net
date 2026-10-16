---
title: "Technology Moats in the AI Era"
meta_title: ""
description: "As AI makes features easier to reproduce, what keeps customers choosing a product? A personal view of technology moats through technical difficulty and business foundations."
date: 2026-10-16T02:04:00+09:00
lastmod: 2026-10-16T02:04:00+09:00
image: "/images/posts/technology-moats-in-the-ai-era/cover.webp"
categories: ["AI"]
tags: ["ai-agents", "software", "competition", "data", "platforms"]
author: "whackur"
translationKey: "technology-moats-in-the-ai-era"
draft: false
---

## Replicating a product and recreating a business are different things

I recently attended an AI conference. As I looked at the many products and demonstrations, one question kept coming back to me.

“How many of these products could I build something similar to through vibe coding?”

This was only my subjective impression from the exhibits and demos, but it seemed that I could implement a substantial share of the core functionality of around 80–90% of them, even if I couldn't reproduce them perfectly.

Of course, building a prototype that behaves similarly is different from building a product that actual customers can trust and use. Visible features alone don't tell us how well a product performs, how reliable or secure it is, or how mature its operations are. But one thing seems clear: anyone can now implement software to a fairly convincing level.

**Does that mean software has no value?**

## The barriers to building and analyzing software are both falling

Something recently made me feel I couldn't keep putting off writing about this question: [REA (Reverse Engineer Anything)](https://github.com/morluto/rea). REA connects AI agents to reverse engineering tools, helping them analyze the structure and behavior of programs without source code and reimplement similar functionality.

Previously, this kind of analysis required a reverse engineering specialist to work directly with tools such as IDA Pro and trace a program's structure. Now you can ask an agent, “Analyze how this particular feature works in this product, and implement something similar in my project.”

Instead of the user operating the analysis tools directly, the agent uses tools such as IDA, Ghidra, and Hopper connected through REA, interprets the results, and continues from analysis into implementation. This doesn't mean every program can be analyzed or reproduced perfectly. But the way we approach understanding and reimplementing existing software is changing.

Attempts to modify games or move them to other environments also caught my attention. Examples include [a demonstration combining Minecraft with Elden Ring](https://www.youtube.com/watch?v=PnJ0XTHM06A) and [AnyPS5](https://github.com/boykopovar/AnyPS5), a project for porting PS5 executables to Windows and Linux.

{{< youtube-lite id="PnJ0XTHM06A" >}}

Over the past year, I've also felt the pace of product launches and improvements accelerate considerably. I expect it to get faster still.

If these changes continue, it will become increasingly difficult to assume that a feature you worked hard to implement will remain difficult for competitors to build for very long.

Where, then, will the technology moats of software remain?

## Being able to write the code doesn't mean being able to obtain the data

Another case to consider is NAVER's shutdown of its Shopping Search API.

NAVER **[announced](https://developers.naver.com/notice/article/32564) that the Shopping Search API offered through its developer center would shut down on July 31, 2026.** It also [explained](https://developers.naver.com/notice/article/32530) that some APIs, including Shopping Insight, would move to NAVER API HUB, but the Shopping Search API would be excluded from that migration and no replacement API would be provided.

Even if you build a similar product search interface and price comparison feature, you still have to obtain and continually update the product information that fills them. AI writing the code for you doesn't also grant you access to another platform's data.

**We need to ask both “What is difficult to implement?” and “Even if we implement it, what will be difficult to obtain?”**

📎 [Data Enclosure and Platform Monopolization in the AI Era](https://blog.hakhub.net/blog/ai-data-enclosure-platform-monopolization/)
This article examines how the end of data access, restrictions on use, contracts, and pricing affect platform competition through NAVER's Shopping Search API shutdown and cases involving Reddit, X, and Cloudflare.

## Six things that are difficult to reproduce

### 1. Platforms with established user networks and customer access

Building a platform's interface and features is different from securing the users and trading relationships active within it.

What matters here is more than the number of registered users. It is the connections between them, their accumulated transaction histories and reputations, and the reasons they find it difficult to move to another service. You may be able to build a similar platform, but you can't bring its users and trading ecosystem along with it.

You also need to look at how a business reaches customers. A company that can introduce a new feature within a product its customers already use starts from a different position than one that must persuade people to find, install, and buy a separate product. Implementing the same feature doesn't give you the same access to customers.

So when I evaluate a platform, I ask about more than its user count. Why do users stay? How easily can it deliver a new product to existing customers?

The question is: **If a competitor offered the same product on the same terms, would customers have a reason to switch?**

### 2. Businesses that require infrastructure and computing resources at scale

Writing the code that runs a service and securing the resources to operate it at the desired scale and cost are separate problems.

In this area, you need to consider computing resources as well as electricity, space, procurement capabilities, and operating experience. Even if you implement similar functionality, whether you can deliver the same throughput and reliability at the same cost needs a separate assessment.

But if anyone can rent those resources on the same terms, simply using a lot of them doesn't necessarily create a strong moat. A large investment and a business that is difficult for competitors to catch up with are different things.

You need to look for technology that delivers higher performance from the same resources, supply terms that others struggle to secure, and an operating structure that becomes more advantageous as it scales.

What matters more than the number of machines is **the foundation for securing those resources and operating them competitively**.

### 3. Products that combine hardware and software

At the conference, **products that combined hardware and software looked much harder to replicate to me than products that offered software alone.**

Along with implementing similar functionality in code, you have to make it work reliably on an actual device. Even if you reproduce the software, you still need to solve problems involving physical performance and durability, component supply, production and quality control, and maintenance.

Take robots. Building software that assesses a situation and issues instructions is different from building a robot that moves as intended in a real environment. Even the same command in code can produce different results depending on a device's design and performance, and the environment in which it is used. Hardware and software have to be adjusted and tested together.

Of course, including hardware doesn't automatically give every product a strong moat. If anyone can assemble the same components and achieve similar quality, the barrier may not be very high.

**Even with off-the-shelf components, turning hardware and software into a complete product and supplying it reliably leaves challenges that code alone can't solve.** To me, that difference alone seemed reason enough to see these products as harder to replicate than software-only products.

### 4. Data and learning processes that competitors can't easily acquire

Think of a company's transaction records, customer support conversations, and cases of problems solved in the field. You may be able to build a similar analytics program, but that doesn't give you another company's years of real operational data.

The same applies to blockchain anti-money laundering (AML). Reading public transaction records is different from identifying which addresses are connected to exchanges or criminal activity. Analytics companies such as Chainalysis combine transaction records with separately researched and verified information to connect addresses to real entities. [Chainalysis](https://www.chainalysis.com/glossary/wallet-attribution/?utm_source=chatgpt.com)

If a company can also establish what transactions it had flagged as risky actually were, and feed those findings into subsequent analysis, its competitive position can become stronger. Competitors have to reproduce the process of acquiring and verifying information as well as the program itself.

**The moat lies in a process through which information others struggle to obtain keeps accumulating and improving the product, as well as in the amount of data.**

### 5. The qualifications to operate a business and the rights to use data

Being able to build a service doesn't immediately qualify you to run that business. Obtaining the necessary approvals and meeting security requirements and contractual conditions remain separate tasks.

For example, operating a virtual asset exchange in South Korea requires filing a report with the Korea Financial Intelligence Unit (FIU) and having it accepted, along with staffing and management systems for anti-money laundering work. Building a trading interface or an AML program doesn't qualify you to operate an exchange. [Financial Services Commission](https://www.fsc.go.kr/no010101/87521)

This foundation can interact with the data moat discussed earlier. **Companies with an advantage in data and technology can meet the necessary security and operating requirements to expand their cooperation with institutions. Conversely, institutions that already have the qualifications to operate and an established customer base can develop their analytical technology using operational data they are legally entitled to use.**

Data creates business opportunities, and the business foundation creates further opportunities to accumulate data. When the two combine, competitors have to reproduce the same functionality as well as **the means of obtaining data and the foundation for using it in a business**.

### 6. Systems deeply integrated into customers' work, and switching costs

Imagine replacing the approval workflow or accounting system your company uses. Even if a new product is cheaper and has a more convenient interface, replacing the existing one immediately isn't easy.

Even a single business travel expense claim may connect departmental approval chains, company reimbursement policies, corporate card records, and accounting processes. Changing the system means migrating historical records, reestablishing those connections, and teaching employees how to use it.

The person responsible has to ask more than “How good are the new features?” They also need to check “Could this delay month-end expense processing?” and “Will we still be able to retrieve existing approval documents?” There are replacement costs and operational risks that don't appear in a product's price.

A competing product may therefore need to offer more than slightly better features or a slightly lower price. It has to be better by enough to justify the effort and risk of switching.

**Here, the moat lies in the way the company already works around the product, beyond the familiarity of its interface.**

## Technology replication difficulty and business foundation difficulty

The difficulty of implementing a product and the difficulty of establishing the foundations for doing business with it are different things. The moats discussed above can be considered along these two axes.

**The X axis is “Technology replication difficulty.”** It describes how difficult it is to implement the same functionality, performance, efficiency, and reliability.

**The Y axis is “Business foundation difficulty.”** It describes how difficult it is to secure the necessary data, infrastructure, supply chains, legal rights, customer relationships, and trust.

![A conceptual diagram separating technology replication difficulty from business foundation difficulty](/images/posts/technology-moats-in-the-ai-era/moat-axes-en.svg)

*The examples are placed to illustrate the concepts, not to assign industry scores or objective rankings. Positions can vary by company and product, even within the same field.*

Implementing an approval workflow feature is different from reproducing its established position within a customer's approval and accounting processes. Products such as robots, which require design and control technology alongside production and supply capabilities, can have barriers on both axes.

This distinction isn't intended to assign fixed scores to industries. It is a way to examine **whether competitors struggle to catch up because of the technology, the business foundation, or both**.

## Software isn't losing its value, but we now need to think before building

AI making some features easier to implement doesn't mean technology loses its value. Technology that delivers high performance and reliability at lower cost, or solves problems that remain unsolved, still matters.

But **being able to build a feature is no longer enough to explain a business's competitiveness.** Securing the necessary data and rights, becoming part of customers' work, and earning trust through real operations still remain.

Of course, these business foundations aren't permanent moats either. AI can reduce the cost of changing systems, and trust can weaken when operations and responses fall short of expectations. A competitor may also emerge that solves the customer's problem differently, without copying the existing product.

The moat lies in **the reasons a product remains difficult to replace even after others build the same functionality**, beyond features that others can't build.

**“If someone builds exactly the same features tomorrow, why would customers keep choosing this product?”**
