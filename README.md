# A Graph-Theoretical Approach to Information Adoption in Narrative Structures

**Authors:**

**Una Joh** - Schoolo of Information Studies, Syracuse University, Hinds Hall, Syracuse, NY, 13244, USA. Email: sjoh01@syr.edu

**Qiusi Sun** - School of Information Studies, Syracuse University, Hinds Hall, Syracuse, NY, 13244, USA. Email: qsun12@syr.edu 

**Joshua Introne** - School of Information Studies, Syracuse University, Hinds Hall, Syracuse, NY, 13244, USA. Email: jeintron@syr.edu  

**Abstract:** Something about narrative adoption in the context of misinformation.

**Keywords:** keyword1, Keyword2, Keyword3, Keyword4

## Introduction

Understanding the comprehension and assimilation of narrative information remains a cornerstone of cognitive research. Extending on the foundational work by Trabasso et al., which postulates a correlation between memory of story elements and their centrality in a causal network representation, we propose an enriched mathematical model. This model captures the likelihood of adopting an information item considering not just its position in the narrative's causal network, but also the combined effects of social influence and personal alignment.

## Methodology

### Graph Representation

Narratives are conceptualized as a graph $G$, with each story item, denoted $s_i$, being a node. The adjacency matrix $A$ captures the causal relationships in the narrative. Although derived potentially from a directed graph, our emphasis is solely on undirected path lengths.

In the following, all equations are written from the perspective of a single agent $p_n$.

### Narrative Influence (W)

The potential influence of a story element $s_i$ based on its position in the narrative is given by:

$$W(s_i) = \frac{1}{|S_t|} \sum_{s_j \in S_t} \frac{1}{d(s_i, s_j) + 1}$$

where $S_t$ is the set of story items adopted by $p_n$ at time $t$ and $d(s_i, s_j)$ is the distance between story items $s_i$ and $s_j$ in the narrative graph.

### Social Influence (I)

The influence of social adoption is described as:

$$ I(s_i) = \frac{2}{1 + e^{-\iota n_i}} -1$$

where $n_i$ is the number of neighbors of $p_n$ that have already adopted the story item $s_i$.

### Alignment (A)

The individual alignment of $p_n$ with a story element is:

$$ A(s_i) = \frac{1 + a_i}{2} $$

where $a_i$ is the alignment value of the story item, ranging from -1 to 1.

### Adoption Probability

Given the weights $\alpha$, $\beta$, and $\gamma$ with the constraint $\alpha + \beta + \gamma = 1$:

$$ P'(s_{i,t+1}|S_t,A) = \alpha W(s_i) + \beta I(s_i) + \gamma A(s_i) $$

## Discussion

This model offers a holistic view of narrative adoption, entwining story structure with social dynamics and personal beliefs. While eigenvector and betweenness centrality provide insights into network positioning, our model enriches this understanding by accounting for external influences and intrinsic inclinations.

## Conclusion

In capturing the nuances of narrative comprehension and assimilation, our approach provides a comprehensive framework that unifies the causal network of a narrative, social context, and personal alignment. It paves a way for a deeper understanding and a more refined analysis of narrative adoption processes in varied contexts.
