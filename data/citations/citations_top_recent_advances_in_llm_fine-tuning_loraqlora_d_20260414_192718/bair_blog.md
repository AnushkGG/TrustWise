# BAIR Blog

**Source URL:** [https://bair.berkeley.edu/blog/](https://bair.berkeley.edu/blog/)
**Scraped Page:** [https://bair.berkeley.edu/blog/](https://bair.berkeley.edu/blog/)
**Title:** BAIR Blog
**Scraped At:** 2026-04-14T19:29:11.556775Z

---

#  [Identifying Interactions at Scale for LLMs](https://bair.berkeley.edu/blog/2026/03/13/spex/)
#####  [Landon Butler](https://landonbutler.github.io/), [Justin Singh Kang](https://justinkang221.github.io), [Yigit Efe Erginbas](https://erginbas.github.io/), [Abhineet Agarwal](https://aagarwal1996.github.io/), [Bin Yu](https://binyu.stat.berkeley.edu/), [Kannan Ramchandran](https://people.eecs.berkeley.edu/~kannanr/) Mar 13, 2026
Understanding the behavior of complex machine learning systems, particularly Large Language Models (LLMs), is a critical challenge in modern artificial intelligence. Interpretability research aims to make the decision-making process more transparent to model builders and impacted humans, a step toward safer and more trustworthy AI. To gain a comprehensive understanding, we can analyze these systems through different lenses: **feature attribution** , which isolates the specific input features driving a prediction ([Lundberg & Lee, 2017](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html); [Ribeiro et al., 2022](https://dl.acm.org/doi/abs/10.1145/2939672.2939778)); **data attribution** , which links model behaviors to influential training examples ([Koh & Liang, 2017](https://proceedings.mlr.press/v70/koh17a/koh17a.pdf); [Ilyas et al., 2022](https://proceedings.mlr.press/v162/ilyas22a/ilyas22a.pdf)); and **mechanistic interpretability** , which dissects the functions of internal components ([Conmy et al., 2023](https://papers.nips.cc/paper_files/paper/2023/hash/34e1dbe95d34d7ebaf99b9bcaeb5b2be-Abstract-Conference.html); [Sharkey et al., 2025](https://openreview.net/forum?id=91H76m9Z94)).
[Continue](https://bair.berkeley.edu/blog/2026/03/13/spex/)
#  [Information-Driven Design of Imaging Systems](https://bair.berkeley.edu/blog/2026/01/10/information-driven-imaging/)
#####  [Henry Pinkard](https://henrypinkard.github.io/), [Leyla Kabuli](https://Lakabuli.github.io/), [Eric Markley](https://emarkley.github.io/), Tiffany Chien, [Jiantao Jiao](https://people.eecs.berkeley.edu/~jiantao/), [Laura Waller](https://www2.eecs.berkeley.edu/Faculty/Homepages/waller.html) Jan 10, 2026
_An encoder (optical system) maps objects to noiseless images, which noise corrupts into measurements. Our information estimator uses only these noisy measurements and a noise model to quantify how well measurements distinguish objects._
Many imaging systems produce measurements that humans never see or cannot interpret directly. Your smartphone processes raw sensor data through algorithms before producing the final photo. MRI scanners collect frequency-space measurements that require reconstruction before doctors can view them. Self-driving cars process camera and LiDAR data directly with neural networks.
What matters in these systems is not how measurements look, but how much useful information they contain. AI can extract this information even when it is encoded in ways that humans cannot interpret.
[Continue](https://bair.berkeley.edu/blog/2026/01/10/information-driven-imaging/)
#  [RL without TD learning](https://bair.berkeley.edu/blog/2025/11/01/rl-without-td-learning/)
#####  [Seohong Park](https://seohong.me/) Nov 1, 2025
In this post, I’ll introduce a reinforcement learning (RL) algorithm based on an “alternative” paradigm: **divide and conquer**. Unlike traditional methods, this algorithm is _not_ based on temporal difference (TD) learning (which has [scalability challenges](https://seohong.me/blog/q-learning-is-not-yet-scalable/)), and scales well to long-horizon tasks.
_We can do Reinforcement Learning (RL) based on divide and conquer, instead of temporal difference (TD) learning._
[Continue](https://bair.berkeley.edu/blog/2025/11/01/rl-without-td-learning/)
#  [What exactly does word2vec learn?](https://bair.berkeley.edu/blog/2025/09/01/qwem-word2vec-theory/)
#####  [Dhruva Karkada](https://dkarkada.xyz/), [Jamie Simon](https://james-simon.github.io/), [Yasaman Bahri](https://research.google.com/pubs/YasamanBahri.html), [Mike DeWeese](https://physics.berkeley.edu/people/faculty/michael-deweese) Sep 1, 2025
What exactly does `word2vec` learn, and how? Answering this question amounts to understanding representation learning in a minimal yet interesting language modeling task. Despite the fact that `word2vec` is a well-known precursor to modern language models, for many years, researchers lacked a quantitative and predictive theory describing its learning process. In our new [paper](https://arxiv.org/abs/2502.09863), we finally provide such a theory. We prove that there are realistic, practical regimes in which the learning problem reduces to _unweighted least-squares matrix factorization_. We solve the gradient flow dynamics in closed form; the final learned representations are simply given by PCA.
_[**Learning dynamics of word2vec**](https://arxiv.org/abs/2502.09863). When trained from small initialization, word2vec learns in discrete, sequential steps. Left: rank-incrementing learning steps in the weight matrix, each decreasing the loss. Right: three time slices of the latent embedding space showing how embedding vectors expand into subspaces of increasing dimension at each learning step, continuing until model capacity is saturated._
[Continue](https://bair.berkeley.edu/blog/2025/09/01/qwem-word2vec-theory/)
#  [Whole-Body Conditioned Egocentric Video Prediction](https://bair.berkeley.edu/blog/2025/07/01/peva/)
#####  [Yutong Bai](https://yutongbai.com/), [Danny Tran](https://dannytran123.github.io/), [Amir Bar](https://www.amirbar.net/), [Yann LeCun](http://yann.lecun.com/), [Trevor Darrell](https://people.eecs.berkeley.edu/~trevor/), and [Jitendra Malik](https://people.eecs.berkeley.edu/~malik/) Jul 1, 2025
_[**Predicting Ego-centric Video from human Actions (PEVA)**](https://arxiv.org/abs/2506.21552). Given past video frames and an action specifying a desired change in 3D pose, PEVA predicts the next video frame. Our results show that, gi

... (truncated)
