{{/* vim: set filetype=mustache: */}}

{{- define "imagePullSecret" }}
{{- with .Values.imagePullSecret }}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\",\"auth\":\"%s\"}}}" .server .username .password .email (printf "%s:%s" .dockerUsername .dockerPassword | b64enc) | b64enc }}
{{- end }}
{{- end }}
