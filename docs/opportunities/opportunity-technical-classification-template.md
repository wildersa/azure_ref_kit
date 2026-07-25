# Opportunity Technical Classification Extension

Use this extension together with `opportunity-template.md` for every new opportunity and every materially revalidated opportunity.

Insert the following sections after `Classification` and after `Data, feedback, and integration assumptions`.

## Technical classification

```yaml
technical_focus: <focus selected for the discovery round>

technical_class:
  - <one or more technical-focus IDs>

model_strategy:
  - <custom-trained | fine-tuned | pretrained | rag-grounded | simulation-trained | optimization-with-learned-components | rules-plus-model | hybrid>

candidate_model_families:
  - <candidate family, not a predetermined algorithm>

learning_paradigm:
  - <supervised | unsupervised | self-supervised | semi-supervised | contextual-bandit | reinforcement-learning | causal-inference | no-custom-training | hybrid>

data_modalities:
  - <tabular | time-series | event | text | document | image | video | audio | graph | spatial | multimodal>

interaction_pattern:
  - <batch | online | streaming | real-time | edge | conversational | asynchronous | human-in-the-loop>

training_requirement: <required | optional | not-required>

data_readiness: <ready | viable-with-data-work | pilot-data-needed | not-currently-trainable | knowledge-base-required | not-applicable>
```

### Technical-focus fit

- **Process signals sought by the round:**
- **Signals actually found in the simulation:**
- **Why this technical class fits the selected decision or exception:**
- **Simpler model or deterministic alternatives tested:**
- **Candidate families rejected and why:**
- **Why the focus did not predetermine the solution:**

## Training-data analysis

This section is mandatory when `model_strategy` contains `custom-trained` or `fine-tuned`, when `training_requirement` is `required`, or when the primary mechanism depends on learned prediction, sequence modeling, specialized neural networks, recommendation, causal or uplift learning, bandits, reinforcement learning, or learned forecasting.

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

For every field, distinguish confirmed information, simulation assumptions, and unknowns. Do not invent dataset size, label quality, balance, coverage, or availability.

For trainable approaches, `data_readiness` must be exactly one of:

```text
ready
viable-with-data-work
pilot-data-needed
not-currently-trainable
```

For pretrained LLM or RAG cases without custom training, explain the knowledge-base, grounding, evaluation-set, update, privacy, and retrieval-quality requirements in the normal data section and use `knowledge-base-required` when appropriate.