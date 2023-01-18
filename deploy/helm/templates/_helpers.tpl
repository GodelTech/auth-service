{{/* vim: set filetype=mustache: */}}

{{- define "imagePullSecret" }}
{{- with .Values.imagePullSecret }}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\",\"auth\":\"%s\"}}}" .server .username .password .email (printf "%s:%s" .dockerUsername .dockerPassword | b64enc) | b64enc }}
{{- end }}
{{- end }}


{{- define "identity-server-poc.redis.fullname" -}}
{{- if .Values.redis.enabled -}}
{{- $name := default "redis" .Values.redis.nameOverride -}}
{{- printf "%s-%s-%s" .Release.Name $name "master"| trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- .Values.redis.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
