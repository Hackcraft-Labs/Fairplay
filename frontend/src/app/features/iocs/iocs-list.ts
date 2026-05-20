import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { IocService } from '../../core/services/ioc';
import { Ioc } from '../../core/models/ioc';
import { CardComponent } from '../../shared/components/card/card';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state';

@Component({
	selector: 'fp-iocs-list',
	standalone: true,
	imports: [
		CommonModule,
		RouterModule,
		MatTableModule,
		MatButtonModule,
		MatIconModule,
		CardComponent,
		LoadingSpinnerComponent,
		EmptyStateComponent
	],
	templateUrl: './iocs-list.html',
	styleUrl: './iocs-list.scss'
})
export class IocsListComponent implements OnInit {
	private readonly iocService = inject(IocService);

	loading = false;
	displayedColumns = ['name', 'file_hash', 'poll_time', 'active', 'actions'];
	data: Ioc[] = [];

	ngOnInit(): void {
		this.fetch();
	}

	fetch(): void {
		this.loading = true;
		this.iocService.list().subscribe({
			next: iocs => {
				this.data = iocs;
				this.loading = false;
			},
			error: () => {
				this.loading = false;
			}
		});
	}

	getStatusLabel(ioc: Ioc): string {
		return ioc.active !== false ? 'Active' : 'Paused';
	}

	getStatusClass(ioc: Ioc): string {
		return ioc.active !== false ? 'fp-badge fp-badge--success' : 'fp-badge fp-badge--warning';
	}
}
