# Technical Focus Rotation for the Solution Opportunity Radar

## Purpose

This document extends the simulation-first discovery method without replacing it.

The radar now advances through two independent axes:

```text
operational segment
+
technical focus
```

The segment identifies the operating context. The technical focus determines which process characteristics the simulation should deliberately inspect.

The focus is a discovery lens, not a predetermined solution.

```text
correct:
segment + technical focus
→ simulate compatible real work
→ inspect data, feedback, labels, rewards, and decisions
→ compare deterministic and simpler model baselines
→ accept or reject the technical hypothesis

incorrect:
select an algorithm
→ invent a problem that uses it
```

A round may end in `no-new-fit` when the selected focus does not expose a credible process, data path, training path, or measurable intervention.

## Independent cursors

The segment cursor and technical-focus cursor advance once after every completed round, including `no-new-fit`.

They do not reset each other. Completing the segment list does not reset the technical-focus list, and completing the technical-focus list does not reset the segment list.

This creates changing combinations over time instead of evaluating one sector eleven consecutive times.

Example:

```text
round 1: manufacturing + time-series-and-sequence-models
round 2: logistics-transport + classical-supervised-ml
round 3: agriculture + specialized-neural-networks
round 4: energy-utilities + anomaly-and-unsupervised-learning
round 5: telecommunications + llm-agents-and-tool-use
round 6: healthcare + causal-and-uplift-learning
```

## Technical focus rotation

### `classical-supervised-ml`

Look for repeated observations with known outcomes, stable feature availability at decision time, and labels produced by normal operations.

Candidate model families may include linear or generalized linear models, decision trees, random forests, gradient boosting, calibrated classifiers, and interpretable scoring models.

### `anomaly-and-unsupervised-learning`

Look for rare deviations, weak or absent labels, peer-group structure, multivariate operating envelopes, and review feedback that may later create labels.

Candidate model families may include clustering, isolation methods, one-class models, density estimation, autoencoders, and graph anomaly detection.

### `time-series-and-sequence-models`

Look for repeated observations through time, temporal windows, delayed outcomes, degradation, state transitions, seasonality, and future events observable after the prediction point.

Candidate model families may include statistical forecasting, gradient boosting with temporal features, LSTM, GRU, temporal convolution, state-space models, and temporal transformers.

### `specialized-neural-networks`

Look for high-dimensional structure where domain-specific representation learning may outperform generic models: image, video, audio, graph, spatial, waveform, or multimodal signals.

Candidate model families may include CNNs, vision transformers, graph neural networks, autoencoders, multimodal encoders, and domain-specific architectures.

### `small-language-models-and-nlp`

Look for bounded text classification, extraction, matching, routing, or short-form generation where a compact model may be cheaper, faster, more private, or easier to evaluate than a general LLM.

Candidate model families may include compact encoders, sentence transformers, small generative models, fine-tuned classifiers, token classifiers, and domain-specific extractors.

### `conversational-llm-and-rag`

Look for a real conversational task requiring grounded retrieval, source attribution, synthesis across documents, or interactive clarification.

Candidate model families may include pretrained LLMs, embedding models, rerankers, retrieval pipelines, and grounded response models.

### `llm-agents-and-tool-use`

Look for a governed multi-step goal requiring tools, changing state, bounded planning, permissions, checkpoints, and explicit human authority.

Candidate model families may include tool-using LLMs, constrained planner-executor patterns, deterministic workflow plus model routing, and policy-governed agents.

### `recommendation-and-ranking`

Look for repeated candidate sets, observable choice or outcome signals, ranking decisions, constrained eligibility, and measurable value from ordering alternatives.

Candidate model families may include learning-to-rank, matrix factorization, two-tower retrieval, candidate generation plus reranking, and calibrated recommendation models.

### `causal-and-uplift-learning`

Look for interventions where prediction alone is insufficient and the question is which action changes the outcome for which case.

Candidate model families may include uplift trees, causal forests, doubly robust estimation, propensity methods, heterogeneous treatment-effect models, and policy evaluation.

### `bandits-and-reinforcement-learning`

Look for repeated decisions with alternative actions, observable rewards, changing state, delayed effects, exploration constraints, and a safe offline or simulated evaluation path.

Candidate model families may include multi-armed bandits, contextual bandits, offline RL, constrained RL, and simulation-trained policies.

Do not force RL when a one-shot prediction, ranking model, mathematical optimizer, or deterministic policy is sufficient.

### `forecasting-and-optimization`

Look for future demand or capacity combined with constrained planning, allocation, scheduling, routing, inventory, or resource decisions.

Candidate model families may include probabilistic forecasting, mathematical optimization, constraint programming, simulation optimization, and learned forecasts feeding deterministic solvers.

## Candidate model families are hypotheses

The focus selects process signals to inspect. It does not select an algorithm in advance.

For example:

```yaml
technical_focus: time-series-and-sequence-models
candidate_model_families:
  - statistical-forecasting
  - gradient-boosting-with-temporal-features
  - lstm
  - gru
  - temporal-convolution
  - temporal-transformer
```

The brief must compare these candidates with rules, statistical baselines, simpler ML, existing products, and the current process. It may reject every candidate.

Fine-tuning is a `model_strategy`, not a separate mandatory focus. It may be proposed only when domain adaptation, task behavior, latency, size, privacy, or evaluation evidence makes it preferable to prompting, RAG, pretrained inference, or conventional supervised training.

## Mandatory technical tags

Every newly published opportunity must contain the following classification block. Existing opportunities receive it when materially revalidated or updated; do not perform a speculative bulk backfill without reading each case.

```yaml
technical_focus:

technical_class:
  -

model_strategy:
  -

candidate_model_families:
  -

learning_paradigm:
  -

data_modalities:
  -

interaction_pattern:
  -

training_requirement:

data_readiness:
```

### Allowed taxonomy

`technical_class` uses one or more technical-focus IDs from this document.

`model_strategy` should use the smallest applicable set:

```text
custom-trained
fine-tuned
pretrained
rag-grounded
simulation-trained
optimization-with-learned-components
rules-plus-model
hybrid
```

`learning_paradigm`:

```text
supervised
unsupervised
self-supervised
semi-supervised
contextual-bandit
reinforcement-learning
causal-inference
no-custom-training
hybrid
```

`data_modalities`:

```text
tabular
time-series
event
text
document
image
video
audio
graph
spatial
multimodal
```

`interaction_pattern`:

```text
batch
online
streaming
real-time
edge
conversational
asynchronous
human-in-the-loop
```

`training_requirement`:

```text
required
optional
not-required
```

`data_readiness`:

```text
ready
viable-with-data-work
pilot-data-needed
not-currently-trainable
knowledge-base-required
not-applicable
```

## Mandatory training-data analysis

The full training-data analysis is required when any of these is true:

- `model_strategy` includes `custom-trained` or `fine-tuned`;
- `training_requirement` is `required`;
- the primary mechanism uses supervised ML, a specialized neural network, sequence learning, recommendation, causal or uplift learning, contextual bandits, reinforcement learning, or a learned forecasting component.

Use this exact structure:

```yaml
training_data:
  observation_unit:
  input_data:
  target_or_reward:
  label_source:
  prediction_time:
  expected_volume:
  class_balance:
  historical_coverage:
  train_validation_split:
  leakage_risks:
  representativeness_risks:
  feedback_loop:
  privacy_and_usage_constraints:
  fallback_if_data_is_insufficient:
```

The analysis must explain what is known, assumed, or unknown. It must not invent volume, label quality, class balance, or historical coverage.

### Readiness classification

For trainable approaches, choose exactly one:

```text
ready
viable-with-data-work
pilot-data-needed
not-currently-trainable
```

`not-currently-trainable` does not automatically reject the business problem. It rejects or redesigns the current training hypothesis unless a bounded data-collection, simulation, weak-supervision, transfer-learning, or pretrained-model path remains credible.

## Portfolio coverage targets

Coverage targets guide investigation over a rolling technical-focus cycle. They are not publication quotas.

```yaml
coverage_targets:
  custom_training_minimum_share: 0.35
  pretrained_or_rag_maximum_share: 0.45
  experimental_rl_or_causal_minimum_per_cycle: 1
```

Interpretation:

- at least 35% of investigated rounds should seriously test a custom-training or fine-tuning path;
- no more than 45% should default their primary investigated mechanism to pretrained LLM or RAG;
- every complete technical-focus cycle should investigate at least one credible RL, bandit, causal, or uplift process.

A round may still publish `no-new-fit`. Never manufacture an opportunity to satisfy a target.

## State and history

Every run records both axes in state and history:

```yaml
segment:
technical_focus:
technical_focus_result: fit | rejected | no-compatible-process | insufficient-data-path
```

When an opportunity is published, history also records:

```yaml
model_strategy:
training_requirement:
data_readiness:
```

The watcher advances both cursors only after repository integrity checks and the round result are persisted.