{{/* vim: set filetype=mustache: */}}

{{/*
Expand the name of the chart.
*/}}
{{- define "identity-server-poc.name" -}}
{{- default .Chart.Name .Values.name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "identity-server-poc.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.name -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "identity-server-poc.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "identity-server-poc.imagePullSecret" }}
{{- printf "{\"auths\": {\"%s\": {\"auth\": \"%s\"}}}" .Values.image.registry (printf "%s:%s" .Values.image.username .Values.image.password | b64enc) | b64enc }}
{{- end }}

{{- define "identity-server-poc.containerImage" }}
{{- printf "%v/%v:%v" .Values.image.registry .Values.image.repository .Values.image.tag }}
{{- end }}

{{- define "identity-server-poc.imagePullSecrets.name" }}
{{- $name := required "A valid .Values.image.pullSecret.name entry required!" .Values.image.pullSecret.name -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "identity-server-poc.redis.fullname" -}}
{{- if .Values.redis.enabled -}}
{{- $name := default "redis" .Values.redis.nameOverride -}}
{{- printf "%s-%s-%s" .Release.Name $name "master"| trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Values.redis.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/* Generate configuration for application */}}
{{- define "identity-server-poc.secretData" }}
  redis:
    password: {{ required "A valid .Values.redis.password entry required!" .Values.redis.password }}
{{- end -}}

{{/* Generate configuration for application */}}
{{- define "identity-server-poc.configData" }}
{
  "{{ .Values.environment_name }}": {
    "hosts": {
        "host": "{{ .Values.hosts.host }}",
    },
    "security": {
        "secret_key": "{{ .Values.security.secret_key }}"
    },
    "db": {
        "uri" : "{{ .Values.db.uri }}"
    },
    "redis": {
        "user": "default",
        "host": "{{ template "identity-server-poc.redis.fullname" . }}",
        "port": "{{ .Values.redis.master.port }}",
        "password": "{{ .Values.redis.password }}",
        "cache_db": 0
    },
  }
}
{{- end -}}
