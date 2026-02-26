AeroShift
AeroShift is a machine learning framework for detecting distribution shifts in aircraft arrival trajectory behavior using unsupervised clustering.
The system extracts geometric and kinematic features from flight trajectories, learns recurring behavioral patterns, and monitors changes in their distribution over time.

1. Overview
Airspace operations generate large volumes of trajectory data. Subtle shifts in arrival behavior can indicate changes in:
Air traffic control procedures
Weather conditions
Airspace congestion
Operational constraints
AeroShift models arrival trajectories as behavioral feature vectors and applies unsupervised clustering to identify recurring operational patterns. It then evaluates distributional changes across time windows to detect systemic behavioral shifts.
The framework is designed as a modular research pipeline, separating feature engineering, clustering, and shift detection components.