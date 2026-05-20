import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { IocService } from '../../core/services/ioc';
import { Ioc } from '../../core/models/ioc';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';

@Component({
	selector: 'fp-ioc-detail',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		MatButtonModule,
		MatIconModule,
		CardComponent,
		LoadingSpinnerComponent
	],
	templateUrl: './ioc-detail.html',
	styleUrl: './ioc-detail.scss'
})
export class IocDetailComponent implements OnInit {
	private readonly route = inject(ActivatedRoute);
	private readonly router = inject(Router);
	private readonly iocService = inject(IocService);

	ioc?: Ioc;
	loading = false;

	get nameParam(): string | null {
		return this.route.snapshot.paramMap.get('name');
	}

	ngOnInit(): void {
		const name = this.nameParam;
		if (!name) {
			this.router.navigate(['/iocs']);
			return;
		}

		this.loading = true;
		this.iocService.get(name).subscribe({
			next: ioc => {
				this.ioc = ioc;
				this.loading = false;
			},
			error: () => {
				this.loading = false;
				this.router.navigate(['/iocs']);
			}
		});
	}

	delete(): void {
		if (!this.ioc || !confirm('Delete this IOC? This cannot be undone.')) {
			return;
		}

		this.loading = true;
		this.iocService.delete(this.ioc.name).subscribe({
			next: () => this.router.navigate(['/iocs']),
			error: () => (this.loading = false)
		});
	}

	metadataEntries(ioc: Ioc): [string, unknown][] {
		return Object.entries(ioc.metadata ?? {});
	}
}
