import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';



@Component({
  selector: 'app-agents',
  imports: [CommonModule, MatButtonModule],
  templateUrl: './agents.component.html',
  styleUrl: './agents.component.scss'
})
export class AgentsComponent {
  agents = [
    {
      name: 'Agent Builder',
      description: 'Un agent IA pour construire des projets complexes.',
      image: 'https://via.placeholder.com/300'
    },
    {
      name: 'Agent Assistant',
      description: 'Un assistant IA pour la gestion des tâches quotidiennes.',
      image: 'https://via.placeholder.com/300'
    },
    {
      name: 'Agent Analytique',
      description: 'Un agent IA pour l\'analyse de données et les rapports.',
      image: 'https://via.placeholder.com/300'
    },
    {
      name: 'Agent Créatif',
      description: 'Un agent IA pour la génération de contenu créatif.',
      image: 'https://via.placeholder.com/300'
    }
  ];

  // Méthode pour créer un nouvel agent
  createNewAgent() {
    // Ajoutez ici la logique pour créer un nouvel agent
    console.log('Créer un nouvel agent');
    // Exemple : Rediriger vers une page de création d'agent
    // this.router.navigate(['/create-agent']);
  }
}
