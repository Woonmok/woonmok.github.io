# 🤖 woonmok.github.io 자동화 상태

**최종 업데이트**: 2026-02-21

## 현재 운영 모드

- 핵심 자동화는 **cron 기반**으로 운영
- 이유: 외장 볼륨 경로(`/Volumes/AI_DATA_CENTRE/...`)에 대해 macOS LaunchAgent가 `Operation not permitted`를 내며 실패하는 사례 확인

## 적용된 자동화

### 1) Daily 파이프라인 (wave-tree-news-hub)

- `06:50` `run_perplexity_auto.sh`
- `07:00` `run_daily_bridge.sh`

확인:

```bash
crontab -l
tail -f /Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/logs/cron_perplexity_auto.log
tail -f /Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/logs/cron_daily_bridge.log
```

### 2) Antigravity watchdog

- `*/2 * * * * /bin/zsh /Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io/scripts/ensure_antigravity.sh`
- 중복 실행 방지: `ensure_antigravity.sh`가 `antigravity.py` 프로세스 전체를 먼저 검사

확인:

```bash
pgrep -af antigravity.py
tail -f /Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io/logs/ensure_antigravity_cron.log
```

## 비활성화/참고

- `com.wavetree.antigravity.plist`
- `com.wavetree.news-sync.plist`
- `com.wavetree.news-sync-loop.plist`

위 파일들은 보관용 설정이며, 현재 운영 기준은 cron입니다.
