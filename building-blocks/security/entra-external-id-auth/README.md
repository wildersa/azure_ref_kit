# Entra External ID Auth

Reference identity pattern for customer-facing portals.

## Purpose

Authenticate external users and map them to customer/tenant access without exposing internal Azure subscriptions or resource permissions.

## Rule

Backend APIs must enforce customer/tenant authorization. The portal must not be the authority for access decisions.
