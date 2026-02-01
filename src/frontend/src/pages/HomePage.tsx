import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BookOpen, TrendingUp, Users, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function HomePage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: Search,
      title: 'Natural Language Query',
      description: 'Ask questions in plain English and get instant insights from publication data',
      action: () => navigate('/query'),
      buttonText: 'Try Query',
    },
    {
      icon: TrendingUp,
      title: 'Analytics Dashboard',
      description: 'Visualize publication trends, citations, and research impact',
      action: () => navigate('/analytics'),
      buttonText: 'View Analytics',
    },
    {
      icon: Users,
      title: 'Faculty Insights',
      description: 'Explore faculty publications, collaborations, and h-index metrics',
      action: () => navigate('/query'),
      buttonText: 'Explore',
    },
    {
      icon: BookOpen,
      title: 'Publication Database',
      description: 'Search and browse through comprehensive publication records',
      action: () => navigate('/query'),
      buttonText: 'Browse',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-12">
        <h1 className="text-4xl font-bold tracking-tight">
          SCISLiSA
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          School of Computer and Information Sciences - Library and Scholarly Analytics
        </p>
        <p className="text-muted-foreground max-w-3xl mx-auto">
          Explore publication data, analyze research trends, and gain insights into faculty contributions
          using natural language queries powered by AI.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card key={feature.title} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </div>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={feature.action} className="w-full">
                  {feature.buttonText}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Stats Section */}
      <Card>
        <CardHeader>
          <CardTitle>Database Overview</CardTitle>
          <CardDescription>Current statistics from our publication database</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">1,301</div>
              <div className="text-sm text-muted-foreground">Publications</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">1,090</div>
              <div className="text-sm text-muted-foreground">Authors</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">34</div>
              <div className="text-sm text-muted-foreground">Faculty Members</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
