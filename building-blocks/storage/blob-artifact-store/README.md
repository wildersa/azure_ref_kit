# Blob Artifact Store

Reference storage pattern for pipeline files and generated outputs.

## Purpose

Store raw inputs, intermediate files, generated reports, and customer-downloadable artifacts.

## Rule

The portal should receive safe artifact references or signed links from the API. It should not know storage account internals.
