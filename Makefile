up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

reset:
	docker compose down -v

urls:
	@printf "Local:   http://localhost:2026\n"
	@ip -4 addr show scope global | awk '/inet / && $$NF !~ /^(docker0|br-)/ { split($$2, ip, "/"); printf "Network: http://%s:2026\n", ip[1] }'
