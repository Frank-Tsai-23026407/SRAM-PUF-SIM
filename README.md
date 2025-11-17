# SRAM-PUF-SIM

A simulator and advanced feature simulation environment for SRAM based PUF (Physical Unclonable Functions).

## About PUFs

A Physical Unclonable Function (PUF) is a physical entity that is embodied in a physical structure and is easy to evaluate but hard to predict. An individual PUF device must be easy to make but practically impossible to duplicate, even if the exact manufacturing process is known. This makes them suitable for applications such as secure key generation and anti-counterfeiting.

## SRAM PUFs

SRAM-based PUFs leverage the unpredictable nature of SRAM cells upon startup. Each SRAM cell has a preferred state (0 or 1) when powered on, which is determined by random manufacturing variations. This pattern of 0s and 1s is unique to each chip and can be used as a fingerprint.

## This Simulator

This project provides a simulation environment for SRAM-based PUFs. It allows for the modeling and analysis of SRAM start-up behavior and the simulation of advanced PUF features.

## Getting Started

For a step-by-step guide on how to build and run the simulator, please see [work.md](work.md).
